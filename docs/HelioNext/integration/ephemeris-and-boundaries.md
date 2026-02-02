# Ephemeris and Boundary Policy

- Ephemeris: require de440s.bsp (or chosen default); validate presence with clear error. If not shipping, document download path and checksum.
- Allow ephemeris selection via CLI/ENV if needed; document precision vs size tradeoffs.
- Boundary policy: HelioNext clamps refinement to the requested window and skips out-of-range hits; no fabricated start-of-window events. Legacy projected boundary hits differ—document this.
- If parity projection is ever needed, gate it behind an explicit flag; keep default accurate/clamped behavior.
