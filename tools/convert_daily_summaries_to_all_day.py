#!/usr/bin/env python3
"""Convert daily summary events to all-day in existing ICS files.

This scans ICS files (glob pattern, default calendars/*.ics) and converts events
categorized as "Daily Transit" to all-day events (DATE value, exclusive end the
next day). Other events are left untouched.
"""
from __future__ import annotations

import argparse
import glob
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

from ics import Calendar


def fold_ical_lines(ics_text: str, limit: int = 75) -> str:
    def fold_line(line: str) -> list[str]:
        if not line:
            return [""]
        folded: list[str] = []
        current = ""
        for ch in line:
            candidate = current + ch
            if len(candidate.encode("utf-8")) <= limit:
                current = candidate
                continue
            if current:
                folded.append(current)
            current = " " + ch
        folded.append(current)
        return folded

    raw_lines = ics_text.splitlines()
    folded_lines: list[str] = []
    for raw_line in raw_lines:
        folded_lines.extend(fold_line(raw_line))
    return "\r\n".join(folded_lines) + "\r\n"


def convert_daily_events(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    cal = Calendar(text)
    changed = False

    for ev in list(cal.events):
        categories = set(ev.categories or [])
        if "Daily Transit" not in categories:
            continue
        if not ev.begin:
            continue

        day: date = ev.begin.date()
        ev.begin = day  # VALUE=DATE start
        ev.end = None
        try:
            ev.make_all_day()
        except Exception:
            pass
        try:
            ev.end = ev.begin + timedelta(days=1)
        except Exception:
            ev.end = day + timedelta(days=1)
        changed = True

    if changed:
        serialized = cal.serialize()
        path.write_text(fold_ical_lines(serialized), encoding="utf-8")
    return changed


def iter_files(patterns: Iterable[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    for pattern in patterns:
        for match in glob.glob(pattern):
            p = Path(match).resolve()
            if p.is_file() and p not in seen:
                seen.add(p)
                yield p


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Daily Transit events to all-day")
    parser.add_argument(
        "--glob",
        dest="patterns",
        nargs="+",
        default=["calendars/*.ics"],
        help="Glob(s) of ICS files to rewrite (default: calendars/*.ics)",
    )
    args = parser.parse_args()

    for path in iter_files(args.patterns):
        changed = convert_daily_events(path)
        status = "updated" if changed else "no-change"
        print(f"{status}: {path}")


if __name__ == "__main__":
    main()
