from daily_transit.cycles.cache import BoundedCache


def test_bounded_cache_eviction_order():
    cache = BoundedCache(max_entries=2)
    cache[("a", 1)] = 1
    cache[("b", 2)] = 2
    cache[("c", 3)] = 3  # evicts oldest (a)

    assert ("a", 1) not in cache
    assert cache.evictions == 1
    # Access updates recency
    _ = cache.get(("b", 2))
    cache[("d", 4)] = 4  # evict c now
    assert ("c", 3) not in cache
    assert ("b", 2) in cache
    assert cache.evictions == 2
