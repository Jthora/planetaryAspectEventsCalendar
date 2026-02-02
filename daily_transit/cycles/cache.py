from __future__ import annotations

from collections import OrderedDict
from typing import Any, Iterator, Optional, Tuple


class BoundedCache(OrderedDict):
    """Simple LRU-ish bounded cache keyed by tuples.

    When max_entries is set and the cache exceeds the limit on insert of a new key,
    the oldest item is evicted. Eviction count is tracked for diagnostics.
    """

    def __init__(self, max_entries: Optional[int] = None):
        super().__init__()
        self.max_entries = max_entries
        self.evictions = 0

    def __getitem__(self, key: Any) -> Any:  # type: ignore[override]
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:  # type: ignore[override]
        if key in self:
            value = super().__getitem__(key)
            self.move_to_end(key)
            return value
        return default

    def __setitem__(self, key: Any, value: Any) -> None:  # type: ignore[override]
        if key in self:
            super().__setitem__(key, value)
            self.move_to_end(key)
            return
        super().__setitem__(key, value)
        if self.max_entries is not None and self.max_entries > 0:
            while len(self) > self.max_entries:
                self.popitem(last=False)
                self.evictions += 1

    def __iter__(self) -> Iterator[Any]:  # type: ignore[override]
        return super().__iter__()

    def items(self) -> Iterator[Tuple[Any, Any]]:  # type: ignore[override]
        return super().items()
