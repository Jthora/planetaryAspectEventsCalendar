# Data Flow (Compact Mode)

1) Input parsing: dates, ayanamsa selection (default tropical), lat/lon/elev, aspect scope, precision options (default decimal), ascii-only flag, status/product-id.
2) Detection: scan aspects with selected scope and orb; produce AspectEvent list (tropical longitudes, raw separation, retro flags if available); use fine timing (seconds) as target.
3) Ayanamsa adjust: apply chosen offset to each planet longitude at event time; store adjusted longitudes.
4) Houses: compute Placidus cusps for event time/location; assign house to each planet using adjusted longitudes; cache cusps when possible; fallback to Whole Sign if Placidus fails.
5) Context build: assemble per-planet data (adjusted lon, sign, house, retro indicator); include ayanamsa metadata for debugging if needed.
6) Formatting: build compact summary/description with Z/H, retro markers, precision rules, no interpretations; respect ascii-only; design lines to avoid excessive folding.
7) Serialization: ICS generation, enforce folding at 75 bytes, write to file.

### Data objects
- AspectEvent: time, planet1/planet2, aspect, exact degrees, raw separation, delta, retro flags.
- ZodiacContext: per planet: adjusted longitude, sign, house.

### Touchpoints
- Detection: uses aspect degrees map (major/complete) and orb/step parameters.
- Ayanamsa module: provides offsets; must be deterministic for given datetime.
- House calculator: Placidus cusps from lat/lon/elev + time.
- Formatter: consumes context and aspect events; outputs compact strings.
