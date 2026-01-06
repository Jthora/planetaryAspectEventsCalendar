# HelioNext Ephemeris and Caching

## Ephemeris Access
- Reuse existing ephemeris provider (Skyfield) via shared adapter; no change of kernels/sources.
- Time conversion policy: consistent UTC handling; avoid repeated conversions of the same timestamp.
- Longitude/position retrieval with ayanamsa applied via shared utilities (ayanamsa = zodiac offset such as galactic center).

## Caching Strategy
- Memoize positions/longitudes at sampled times keyed by body + time (time can be float days or datetime; define format once).
- Cache separation computations for body pairs where reuse is likely (coarse/refine/retro reuse the same samples).
- Lifetime: within a run; sized to date window; avoid unbounded growth (consider LRU if needed).

### Key formats
- Time key: float JD or UTC datetime converted to float days; pick one and keep consistent.
- Body key: stable string or enum matching legacy identifiers.
- Pair key: tuple(sorted(body1, body2)) + time.

### Lifetimes
- Per-run caches cleared at end of execution; scoped to requested date range.
- Optional LRU cap (e.g., 10k entries) if memory measured as an issue on year runs.

## Sample Reuse
- Share samples between coarse, refine, and retro/station checks to minimize ephemeris calls.
- Avoid duplicate ephemeris calls when refining or checking retrograde near an event; prefer interpolating/reusing nearby samples.

### Reuse rules
- If refine bracket already holds positions at t0/t1, reuse them for solver steps and retro checks.
- Allow linear interpolation of positions for intermediate solver steps to reduce calls when safe; fall back to fresh ephemeris if error grows.

## Data Shapes (future batching)
- Define structures that can hold arrays of times/bodies for potential vectorization (e.g., numpy arrays), but keep scalar-friendly interfaces initially.
- Ensure angle wrapping and ayanamsa application work on both scalar and vector inputs.

## Tradeoffs
- Memory vs speed: document expected cache size per day/range (positions per body, separations per pair).
- Eviction policy if needed (e.g., LRU) once memory footprint is measured; start with simple unbounded within-run if safe.

### Estimated footprint (guideline)
- Positions: bodies * samples_per_day * days (e.g., 12 bodies * 96 samples/day * 365 ≈ 420k entries).
- Separations: pairs * samples similar order; monitor and cap if needed.

## Instrumentation
- Cache hit/miss counters for positions and separations; report in perf logs.
- Ephemeris call counts to track effectiveness; correlate with runtime.

### Logging points
- Emit summary: position_cache_hits/misses, separation_cache_hits/misses, ephemeris_calls.
- Optional debug: top N callers causing cache misses.
