#!/usr/bin/env python3
"""Cross-check ICS aspect events against an independent ephemeris source.

Usage example (NASA Horizons backend, requires internet):

    python tools/ics_sanity_check.py \
        --ics output/space_force_jan_2026.ics \
        --reference horizons \
        --output-csv output/reports/space_force_jan_2026_sanity.csv

For an offline dry-run that reuses the local Skyfield ephemeris instead of the
remote Horizons service, swap ``--reference horizons`` with
``--reference skyfield``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, date, time, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
from ics import Calendar

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from daily_transit.constants import EPHEMERIS_NAME_MAP  # noqa: E402

try:  # Optional dependency for live Horizons queries.
    from astroquery.jplhorizons import Horizons  # type: ignore
    from astropy.time import Time  # type: ignore
    import astropy.units as u  # type: ignore
    from astropy.coordinates import SkyCoord, GeocentricTrueEcliptic  # type: ignore
except Exception:  # pragma: no cover - astroquery is optional in CI
    Horizons = None
    Time = None
    u = None
    SkyCoord = None
    GeocentricTrueEcliptic = None

from skyfield.api import load as load_skyfield  # noqa: E402

RETRO_CHARS = {"℞"}
TZ_UTC = timezone.utc

ASPECT_SYMBOL_TO_NAME_AND_DEGREES: Dict[str, Tuple[str, float]] = {
    "\u260c": ("Conjunction", 0.0),
    "\u260d": ("Opposition", 180.0),
    "\u25b3": ("Trine", 120.0),
    "\u25a1": ("Square", 90.0),
    "\u26b9": ("Sextile", 60.0),
    "\u267b": ("Quincunx", 150.0),
    "\u26fa": ("Semisextile", 30.0),
    "\u2220": ("Semisquare", 45.0),
    "\u26bc": ("Sesquiquadrate", 135.0),
    "\u235b": ("Quintile", 72.0),
    "\u2359": ("Biquintile", 144.0),
}
ASPECT_SYMBOL_PRIORITY = sorted(ASPECT_SYMBOL_TO_NAME_AND_DEGREES.keys(), key=len, reverse=True)

PLANET_HORIZONS_IDS: Dict[str, str] = {
    "Sun": "10",
    "Moon": "301",
    "Mercury": "199",
    "Venus": "299",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899",
    "Pluto": "999",
}


@dataclass
class AspectEvent:
    timestamp: datetime
    planet_a: str
    planet_b: str
    aspect_symbol: str
    aspect_name: str
    target_degrees: float
    reported_delta: float
    severity: str
    guidance: str
    raw_line: str


@dataclass
class AspectResult:
    event: AspectEvent
    longitude_a: Optional[float]
    longitude_b: Optional[float]
    separation: Optional[float]
    divergence: Optional[float]
    status: str
    error: Optional[str]


def _normalize_planet(token: str) -> str:
    cleaned = token
    for char in RETRO_CHARS:
        cleaned = cleaned.replace(char, "")
    cleaned = re.sub(r"[^A-Za-z ]", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if cleaned not in PLANET_HORIZONS_IDS:
        raise ValueError(f"Unknown planet label '{token}' after normalization -> '{cleaned}'")
    return cleaned


def _angular_separation(lon_a: float, lon_b: float) -> float:
    diff = (lon_a - lon_b + 180.0) % 360.0 - 180.0
    return abs(diff)


def _parse_aspect_lines(description: str, event_date: date) -> List[AspectEvent]:
    aspects: List[AspectEvent] = []
    lines = description.splitlines()
    capturing = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if not capturing:
            if stripped.startswith("Exact Aspects Today"):
                capturing = True
            continue
        if not stripped:
            break
        if stripped.lower().startswith("no exact"):
            break
        if " - \u0394" not in stripped:
            continue
        try:
            event = _parse_aspect_line(stripped, event_date)
        except ValueError as exc:
            raise ValueError(f"Failed to parse aspect line '{stripped}': {exc}") from exc
        aspects.append(event)
    return aspects


def _parse_aspect_line(line: str, event_date: date) -> AspectEvent:
    prefix, suffix = line.split(" - \u0394", 1)
    prefix = prefix.strip()
    match = re.match(r"(?P<time>\d{2}:\d{2})\s+(?P<body>.+)", prefix)
    if not match:
        raise ValueError("Time + body pattern not found")
    time_str = match.group("time")
    bodies = match.group("body").strip()

    symbol = None
    for candidate in ASPECT_SYMBOL_PRIORITY:
        needle = f" {candidate} "
        if needle in bodies:
            symbol = candidate
            break
    if symbol is None:
        raise ValueError("No aspect symbol present")
    planet_a_raw, planet_b_raw = [part.strip() for part in bodies.split(f" {symbol} ", 1)]
    planet_a = _normalize_planet(planet_a_raw)
    planet_b = _normalize_planet(planet_b_raw)

    aspect_name, target_deg = ASPECT_SYMBOL_TO_NAME_AND_DEGREES[symbol]

    delta_section = suffix.split("\u00b0", 1)
    if len(delta_section) != 2:
        raise ValueError("Missing degree sign in delta section")
    reported_delta = float(delta_section[0])

    remainder = delta_section[1].lstrip(" -")
    severity = ""
    guidance = ""
    if remainder:
        if " \u2014 " in remainder:
            severity, guidance = [part.strip() for part in remainder.split(" \u2014 ", 1)]
        else:
            severity = remainder.strip()

    hour, minute = map(int, time_str.split(":"))
    dt = datetime.combine(event_date, time(hour=hour, minute=minute), tzinfo=TZ_UTC)

    return AspectEvent(
        timestamp=dt,
        planet_a=planet_a,
        planet_b=planet_b,
        aspect_symbol=symbol,
        aspect_name=aspect_name,
        target_degrees=target_deg,
        reported_delta=reported_delta,
        severity=severity,
        guidance=guidance,
        raw_line=line,
    )


class HorizonsBackend:
    def __init__(self, cache_path: Optional[Path] = None):
        if any(dep is None for dep in (Horizons, Time, u, SkyCoord, GeocentricTrueEcliptic)):
            raise RuntimeError("astroquery/astropy is required for the Horizons backend")
        self.cache_path = cache_path
        self.cache: Dict[str, float] = {}
        if cache_path and cache_path.exists():
            self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
        self.location = "500@399"  # Earth geocenter

    def longitude(self, planet: str, timestamp: datetime) -> float:
        key = f"{planet}|{timestamp.isoformat()}"
        if key in self.cache:
            return self.cache[key]

        time_obj = Time(timestamp, scale="utc")
        obj = Horizons(id=PLANET_HORIZONS_IDS[planet], location=self.location, epochs=time_obj.jd)
        eph = obj.ephemerides()
        ra = float(eph["RA"][0])
        dec = float(eph["DEC"][0])
        coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="icrs")
        ecliptic = coord.transform_to(GeocentricTrueEcliptic(equinox=time_obj))
        longitude = float(ecliptic.lon.wrap_at(360 * u.deg).deg)
        self.cache[key] = longitude
        return longitude % 360.0

    def flush(self) -> None:
        if self.cache_path is None:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")


class SkyfieldBackend:
    def __init__(self, ephemeris_path: Path):
        if not ephemeris_path.exists():
            raise FileNotFoundError(f"Ephemeris file not found: {ephemeris_path}")
        self.ts = load_skyfield.timescale()
        self.ephemeris = load_skyfield(str(ephemeris_path))
        self.earth = self.ephemeris["earth"]

    def longitude(self, planet: str, timestamp: datetime) -> float:
        target_name = EPHEMERIS_NAME_MAP[planet]
        body = self.ephemeris[target_name]
        t = self.ts.utc(
            timestamp.year,
            timestamp.month,
            timestamp.day,
            hour=timestamp.hour,
            minute=timestamp.minute,
            second=timestamp.second,
        )
        astrometric = self.earth.at(t).observe(body)
        _, lon, _ = astrometric.apparent().ecliptic_latlon()
        return lon.degrees % 360.0

    def flush(self) -> None:  # interface parity with HorizonsBackend
        return


def _load_aspect_events(calendar: Calendar, categories: Optional[Sequence[str]] = None) -> List[AspectEvent]:
    wanted = {cat.lower() for cat in categories or ("Daily Transit",)}
    events: List[AspectEvent] = []
    for event in sorted(calendar.events, key=lambda e: e.begin):
        event_categories = {c.lower() for c in (event.categories or set())}
        if not event_categories.intersection(wanted):
            continue
        event_date = event.begin.datetime.astimezone(TZ_UTC).date()
        description = event.description or ""
        aspects = _parse_aspect_lines(description, event_date)
        events.extend(aspects)
    return events


def _build_backend(args: argparse.Namespace):
    if args.reference == "horizons":
        cache_path = Path(args.cache) if args.cache else None
        return HorizonsBackend(cache_path=cache_path)
    ephemeris_path = Path(args.ephemeris or PROJECT_ROOT / "de440s.bsp")
    return SkyfieldBackend(ephemeris_path)


def _evaluate(aspects: Sequence[AspectEvent], backend, tolerance: float) -> List[AspectResult]:
    results: List[AspectResult] = []
    for aspect in aspects:
        try:
            lon_a = backend.longitude(aspect.planet_a, aspect.timestamp)
            lon_b = backend.longitude(aspect.planet_b, aspect.timestamp)
            separation = _angular_separation(lon_a, lon_b)
            divergence = abs(separation - aspect.target_degrees)
            status = "PASS" if divergence <= tolerance else "FAIL"
            results.append(
                AspectResult(
                    event=aspect,
                    longitude_a=lon_a,
                    longitude_b=lon_b,
                    separation=separation,
                    divergence=divergence,
                    status=status,
                    error=None,
                )
            )
        except Exception as exc:
            results.append(
                AspectResult(
                    event=aspect,
                    longitude_a=None,
                    longitude_b=None,
                    separation=None,
                    divergence=None,
                    status="ERROR",
                    error=str(exc),
                )
            )
    return results


def _results_to_dataframe(results: Sequence[AspectResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        event = result.event
        rows.append(
            {
                "timestamp": event.timestamp.isoformat(),
                "date": event.timestamp.date().isoformat(),
                "time_utc": event.timestamp.strftime("%H:%M"),
                "planet_a": event.planet_a,
                "planet_b": event.planet_b,
                "aspect_symbol": event.aspect_symbol,
                "aspect": event.aspect_name,
                "target_degrees": event.target_degrees,
                "reported_delta": event.reported_delta,
                "severity": event.severity,
                "guidance": event.guidance,
                "reference_lon_a": result.longitude_a,
                "reference_lon_b": result.longitude_b,
                "measured_separation": result.separation,
                "divergence": result.divergence,
                "status": result.status,
                "error": result.error,
                "source_line": event.raw_line,
            }
        )
    return pd.DataFrame(rows)


def summarize_results(df: pd.DataFrame) -> str:
    total = len(df)
    if total == 0:
        return "No aspects detected in the ICS file."
    passes = int((df["status"] == "PASS").sum())
    failures = int((df["status"] == "FAIL").sum())
    errors = int((df["status"] == "ERROR").sum())
    summary = f"Checked {total} aspects — PASS: {passes}, FAIL: {failures}, ERRORS: {errors}."
    if not df["divergence"].dropna().empty:
        worst = df["divergence"].dropna().max()
        summary += f" Worst divergence: {worst:.3f}°."
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare ICS aspect events with a reference ephemeris.")
    parser.add_argument("--ics", type=Path, required=True, help="Path to the ICS file to inspect.")
    parser.add_argument(
        "--reference",
        choices=("horizons", "skyfield"),
        default="horizons",
        help="Ephemeris backend to use (default: horizons).",
    )
    parser.add_argument(
        "--ephemeris",
        type=Path,
        help="Local .bsp ephemeris file for the skyfield backend (defaults to de440s.bsp).",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=PROJECT_ROOT / "output" / "reports" / "horizons_cache.json",
        help="Cache file for Horizons longitude lookups.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=PROJECT_ROOT / "output" / "reports" / "ics_sanity_report.csv",
        help="Where to write the detailed CSV report.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.35,
        help="Maximum allowed divergence in degrees before flagging a failure (default: 0.35°).",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        help="Optional cap on the number of aspects to evaluate (debugging aid).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.ics.exists():
        print(f"ICS file not found: {args.ics}")
        return 1

    with args.ics.open("r", encoding="utf-8") as handle:
        calendar = Calendar(handle.read())

    aspects = _load_aspect_events(calendar)
    if args.max_events:
        aspects = aspects[: args.max_events]
    if not aspects:
        print("No Daily Transit aspect events detected in the ICS description blocks.")
        return 0

    backend = _build_backend(args)
    results = _evaluate(aspects, backend, tolerance=args.tolerance)
    df = _results_to_dataframe(results)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output_csv, index=False)

    summary = summarize_results(df)
    print(summary)

    if hasattr(backend, "flush"):
        backend.flush()

    fail_count = int((df["status"] == "FAIL").sum()) + int((df["status"] == "ERROR").sum())
    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
