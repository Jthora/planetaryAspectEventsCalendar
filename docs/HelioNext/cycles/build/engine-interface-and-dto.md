# Cycle Engine Interface and DTO

## Event Type Taxonomy (Extensible)
- ingress: sign boundary crossing.
- synodic_phase: configured phase angles (default 0/90/180/270/360) between two bodies.
- retro_interval: interval where a body’s longitudinal rate < 0.
- station: instant where rate crosses zero (forward→retro or retro→forward); may coincide with retro interval edges.
- perihelion/aphelion: distance extrema markers when supported by kernels.
- node/apogee/perigee markers: optional types if kernels provided; **disabled by default in v1** until external kernels are supplied.

## DTO Fields (Core and Type-Specific)
- Core fields: event_type, start_time_utc, end_time_utc (same as start for instants), ayanamsa_mode, schema_version.
- Body fields: body for single-body events; body1/body2 for synodic phases (ordered or sorted, specify policy); optional body_roles if needed later.
- Positional context (optional): sign (for ingress), phase_angle (for synodic), longitude(s) at event time if needed for debugging; wrap to 0–360 after ayanamsa application.
- Motion flags: retrograde (bool), station_direction ("forward_to_retro" | "retro_to_forward"), retro_probe_hours used (for traceability).
- Quality/uncertainty: station_strength/quality (optional scalar or enum), uncertainty_seconds when solver fallback used, convergence_status.
- Distance: distance_au (optional) for perihelion/aphelion; null otherwise.
- Display helpers: summary, label, glyphs (optional) to avoid breaking downstream aspect consumers; can be synthesized later by formatter if omitted.
- Metadata: source_engine (string), computation_notes (optional), merge_window_seconds used, chunk_id if long spans are chunked.

## Required vs Optional per Event Type
- ingress: body, sign, start_time_utc; end_time_utc mirrors start; ayanamsa_mode required. Optional: uncertainty_seconds.
- synodic_phase: body1, body2, phase_angle, start_time_utc; separation_deg required for transparency; optional end_time_utc (instants), uncertainty_seconds, delta_deg.
- retro_interval: body, start_time_utc, end_time_utc, retrograde=true; optional uncertainty_seconds, merge_window_seconds.
- station: body, start_time_utc, station_direction; optional station_strength/quality, uncertainty_seconds.
- perihelion/aphelion: body; optional distance_au, uncertainty_seconds.
- node/apogee/perigee (if enabled): body/point, start_time_utc; optional distance for apogee/perigee, uncertainty_seconds.

### Schema Version Policy
- schema_version is required on all CycleEvent DTOs; baseline `v1` for HelioNext cycles.
- Additive fields (new optional attributes) do not require a version bump; breaking changes (field removal/rename or behavioral shifts) require incrementing schema_version and documenting migration steps in rollout-and-migration.md.
- ICS/JSON serializers must include schema_version and treat unknown fields leniently to preserve forward compatibility.

## Ordering, Sorting, and Merge/Dedupe
- Sort order: UTC time asc, then event_type (stable ordering documented), then (body) or (body1, body2) lexicographically.
- Merge window: configurable per event_type; default small for instants (e.g., ≤5 minutes) and user-configurable for intervals; when colliding, prefer lowest uncertainty then earliest time.
- Collisions: station vs ingress at same instant retained as separate events; dedupe only identical event_type/body/sign/phase within merge window.

## Determinism and Idempotence
- No randomness; caches do not affect ordering; repeated runs with same inputs produce identical DTOs.
- Explicit rounding policy for stored times (full datetime with seconds; sub-second retained internally, serialized with ISO seconds unless configured otherwise).

## Error Contracts and Validation
- Invalid event_type or missing required fields: raise structured validation error (type, field, message).
- Missing kernels/unsupported bodies: emit explicit error code; caller chooses hard-fail or skip.
- Out-of-range times: blocked with boundary error; never fabricate events at window edges.
- Phase list validation: angles must be within [0,360]; duplicates rejected; sorted for deterministic processing.
- Ayanamsa validation: only allowed names; log chosen ayanamsa; tropical default when none provided.

## DTO Versioning and Compatibility
- schema_version field required; start at v1 for cycles; additive fields allowed without breaking consumers that ignore unknown keys.
- Breaking changes require version bump and adapter; document migration guidance.

## Serialization Expectations
- JSON: ISO-8601 UTC timestamps; booleans for flags; floats in degrees; enumerations as strings; null for missing optional fields.
- ICS: mapping defined in ICS schema doc; DTO remains source of truth; ICS generation must not mutate DTO values.

## Traceability and Metrics Hooks
- Include optional computation_notes (e.g., solver fallback used, chunked window id) and merge_window_seconds used for the event.
- Allow attaching metrics summary per run externally; DTO remains lightweight but may include per-event uncertainty_seconds when fallback occurred.
