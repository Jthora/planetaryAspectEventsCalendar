from __future__ import annotations

from typing import Dict


def record_refine_sample(metrics: Dict, entry: Dict, enabled: bool, limit: int = 10) -> None:
    """Keep top-N refinement traces by iteration count when timing debug is enabled."""

    if not enabled:
        return

    samples = metrics.setdefault("refine_samples", [])
    samples.append(entry)
    samples.sort(key=lambda item: item.get("iter_count", 0), reverse=True)
    if len(samples) > limit:
        del samples[limit:]
