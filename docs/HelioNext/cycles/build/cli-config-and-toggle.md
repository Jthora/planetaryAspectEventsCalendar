# CLI, Config, and Toggle

## Goals
- Provide an opt-in path for cycle generation without disturbing existing aspect defaults.
- Keep configuration explicit, validated, and discoverable via CLI help and docs.
- Ensure rollback/off switch remains available in every release.

## Engine Selection
- Flag: --cycle-engine {off,helionext-cycles} (name TBD); default = off.
- Env override: CYCLE_ENGINE or similar; precedence below CLI, above defaults.
- Config file key (if used) mirrors flag name; documented precedence: CLI > env > config > default.
- Validation: fail fast on unknown engine names with list of allowed values.

## Cycle Options
- --cycle-types: comma list (ingress,synodic_phase,retro_interval,station,perihelion,aphelion,node,apogee,perigee); default = ingress,synodic_phase,retro_interval,station.
- --phase-angles: comma list of degrees; validated 0–360; sorted and deduped; default = 0,90,180,270,360.
- --ingress-signs: subset of 12 signs; default = all; validated against standard names/abbrevs.
- --retro-probe-hours: float; default aligns with engine default; bounds checked.
- --cycle-merge-window-hours: float; default small for instants; can be tuned for dedupe.
- --ayanamsa: tropical|lahiri|galactic_core; validated; tropical default.
- --chunk-span-days (optional): max days per processing chunk for long spans; default None (auto).
- --timing-debug / --metrics: enable verbose logging or metrics export; reuse existing patterns.

## Compatibility and Defaults
- Existing aspect flags unchanged; running without cycle flags yields identical behavior to current release.
- Defaults chosen to minimize noise: cycles off, tropical ayanamsa, standard phase list.
- If cycles on but a required kernel is missing, behavior controlled by --missing-body-policy (fail|skip) (optional flag).

## Logging and Observability
- On start, log: active cycle engine, cycle_types, phase_angles, ayanamsa, merge_window, chunk_span, missing-body policy.
- Metrics flag emits JSON summary (runtime, ephemeris_calls, cache stats, refine stats, boundary_drops, skipped_bodies).
- Debug flag prints bracket/refine traces for targeted investigation.

## Examples
- Short ingress run: --cycle-engine helionext-cycles --cycle-types ingress --start 2026-01-01 --end 2026-01-08 --ayanamsa tropical.
- Synodic focus: --cycle-engine helionext-cycles --cycle-types synodic_phase --phase-angles 0,60,90,120,180 --planets "Sun,Moon,Mercury,Venus".
- Retro window: --cycle-engine helionext-cycles --cycle-types retro_interval,station --start 2026-03-01 --end 2026-04-15 --ayanamsa galactic_core.
- Long span chunked: --cycle-engine helionext-cycles --cycle-types ingress,synodic_phase --start 1900-01-01 --end 2000-01-01 --chunk-span-days 365 --missing-body-policy skip.

## Validation and Error Messaging
- Invalid comma lists (bad names, bad angles) produce explicit errors with allowed values.
- If cycles requested but engine off, warn and disable cycles; suggest enabling engine.
- If ayanamsa unsupported, fail with list of supported names.

## Rollback and Safety
- Setting --cycle-engine off (or env override) bypasses cycle pipeline entirely; aspect behavior remains intact.
- Document in migration guide how to disable if issues arise; ensure tests cover off path.

## Docs and Help
- CLI help updated with cycle flag descriptions and defaults; examples included.
- README/snippets in docs reference these flags; link to this doc and rollout/migration notes.
