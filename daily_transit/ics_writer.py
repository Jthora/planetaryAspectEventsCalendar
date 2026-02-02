from __future__ import annotations

from typing import List


def fold_ical_lines(ics_text: str, limit: int = 75) -> str:
    """Fold iCal lines to <= limit bytes per line (RFC 5545 section 3.1)."""

    def fold_line(line: str) -> List[str]:
        if not line:
            return [""]
        folded: List[str] = []
        current = ''
        for ch in line:
            candidate = current + ch
            if len(candidate.encode('utf-8')) <= limit:
                current = candidate
                continue
            if current:
                folded.append(current)
            current = ' ' + ch
        folded.append(current)
        return folded

    raw_lines = ics_text.splitlines()
    folded_lines: List[str] = []
    for raw_line in raw_lines:
        folded_lines.extend(fold_line(raw_line))
    return "\r\n".join(folded_lines) + "\r\n"


def serialize_calendar(events: List, product_id: str) -> str:
    normalized_prodid = product_id if product_id else '-//Daily Transit Aspect Generator//EN'
    if not normalized_prodid.startswith('-//'):
        normalized_prodid = f"-//{normalized_prodid}"
    lines: List[str] = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        f'PRODID:{normalized_prodid}',
        'CALSCALE:GREGORIAN',
    ]
    for event in events:
        event_lines = event.serialize().strip().splitlines()
        lines.extend(event_lines)
    lines.append('END:VCALENDAR')
    raw_text = "\r\n".join(lines)
    if not raw_text.endswith("\r\n"):
        raw_text += "\r\n"
    return raw_text
