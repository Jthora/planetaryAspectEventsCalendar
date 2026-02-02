from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class BodyCoverage:
    start_utc: datetime
    end_utc: datetime


def _to_datetime(ts, jd_value: float) -> datetime:
    """Convert Julian date to naive UTC datetime."""
    return ts.tt_jd(jd_value).utc_datetime().replace(tzinfo=None)


def _segment_window(segment) -> tuple[float, float]:
    start_second = getattr(segment, "start_second", 0.0) or 0.0
    end_second = getattr(segment, "end_second", 0.0) or 0.0
    start_jd = segment.start_jd + start_second / 86400.0
    end_jd = segment.end_jd + end_second / 86400.0
    return start_jd, end_jd


def build_body_coverage_index(eph, ts, eph_keys: Iterable[str]) -> Dict[str, BodyCoverage]:
    """Return coverage windows for each ephemeris key.

    Looks up the SPK target id from the ephemeris entry, then scans the kernel
    segments to find the earliest and latest Julian dates. Raises KeyError if a
    body is absent or lacks segments.
    """

    coverage: Dict[str, BodyCoverage] = {}
    segments = getattr(eph, "spk", None).segments  # type: ignore[attr-defined]
    if segments is None:
        raise KeyError("Ephemeris kernel does not expose SPK segments")

    for eph_key in sorted(set(eph_keys)):
        try:
            position = eph[eph_key]
        except KeyError as exc:  # pragma: no cover - defensive for future kernels
            raise KeyError(f"Ephemeris missing body '{eph_key}'") from exc

        target_id = getattr(position, "target", None)
        if target_id is None:  # pragma: no cover - unexpected for SPK kernels
            raise KeyError(f"Ephemeris entry '{eph_key}' lacks a target id")

        start_jd: Optional[float] = None
        end_jd: Optional[float] = None
        for segment in segments:
            if segment.target != target_id:
                continue
            seg_start_jd, seg_end_jd = _segment_window(segment)
            start_jd = seg_start_jd if start_jd is None else min(start_jd, seg_start_jd)
            end_jd = seg_end_jd if end_jd is None else max(end_jd, seg_end_jd)

        if start_jd is None or end_jd is None:
            raise KeyError(f"No segment coverage found for '{eph_key}' (target {target_id})")

        coverage[eph_key] = BodyCoverage(
            start_utc=_to_datetime(ts, start_jd),
            end_utc=_to_datetime(ts, end_jd),
        )

    return coverage


def validate_range_within_coverage(
    coverage_index: Dict[str, BodyCoverage],
    start_dt: datetime,
    end_dt: datetime,
    *,
    label_by_key: Optional[Dict[str, str]] = None,
):
    """Fail fast if requested range exceeds any body coverage.

    Raises SystemExit with a descriptive message naming the offending body and
    its coverage window when the requested span is out of bounds.
    """

    violations = []
    for eph_key, window in coverage_index.items():
        label = label_by_key.get(eph_key, eph_key) if label_by_key else eph_key
        if start_dt < window.start_utc:
            violations.append(
                f"{label} starts {window.start_utc.date()} (requested {start_dt.date()})"
            )
        if end_dt > window.end_utc:
            violations.append(
                f"{label} ends {window.end_utc.date()} (requested {end_dt.date()})"
            )

    if violations:
        detail = "; ".join(violations)
        raise SystemExit(
            f"Requested range {start_dt.date()} to {end_dt.date()} exceeds ephemeris coverage: {detail}"
        )


def format_coverage_lines(
    coverage_index: Dict[str, BodyCoverage],
    *,
    label_by_key: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Return a mapping of body label to formatted coverage string."""

    lines: Dict[str, str] = {}
    for eph_key, window in coverage_index.items():
        label = label_by_key.get(eph_key, eph_key) if label_by_key else eph_key
        lines[label] = f"{window.start_utc.date()} to {window.end_utc.date()}"
    return lines
