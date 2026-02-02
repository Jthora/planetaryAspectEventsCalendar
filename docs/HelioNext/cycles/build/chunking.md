# Cycle Chunking Policy

- **Default span:** 180 days per chunk with a 12-hour overlap to capture boundary crossings.
- **Dedupe:** Events from overlapping seams are deduplicated using event type, bodies, sign, phase angle, times, ayanamsa, and station flags.
- **Overrides:** Use `--cycle-chunk-span-days` to change span; set 0 or a negative value to disable chunking.
- **Caches:** Position and separation caches are shared across chunks to avoid redundant ephemeris calls.
