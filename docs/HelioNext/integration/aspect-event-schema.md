# AspectEvent Schema Contract

Purpose: Document the fields emitted by aspect detection (legacy and HelioNext) for downstream consumers (ICS builder, titles, interpretations, compact formatter).

Fields (current contract):
- time: datetime (UTC) exact moment of aspect hit
- planet1: str (body name)
- planet2: str (body name)
- aspect: str (aspect name)
- exact_degrees: float (target angle)
- raw_separation: float (actual angular separation at time)
- delta: float (absolute deviation from exact degrees)
- planet1_retrograde: bool
- planet2_retrograde: bool

Assumptions:
- Aspect names follow the catalog in use (major/complete) and may include aliases normalized upstream.
- Time is naive UTC datetime; timezone handling is applied downstream when formatting ICS.
- No house/ayanamsa data is included in AspectEvent; those are computed downstream as context.

Stability:
- Adding new fields should be additive and backward-compatible; existing fields should not be renamed.
- Downstream consumers should not assume any specific ordering of events beyond sorting by time.
