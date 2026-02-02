# Rollout and Risk

- Default remains legacy; provide `--engine helionext` opt-in and optional ENV override.
- Plan staged rollout: start with opt-in runs, then consider flipping default after parity and perf are validated; keep legacy fallback flag.
- Risks: behavior drift (merge/boundary/retro/station), performance regressions, ephemeris availability. Mitigate with diff-harness CI, benchmarks, clear errors, and docs.
- Document known differences and support horizon for the legacy engine once HelioNext is default.
