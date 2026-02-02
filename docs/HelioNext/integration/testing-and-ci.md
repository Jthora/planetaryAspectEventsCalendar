# Testing and CI

- Add CLI integration tests exercising `--engine helionext` to produce ICS without errors.
- Add generator-helper tests selecting helionext to ensure events flow into ICS builder.
- Reuse diff-harness tests (short/week/medium) to guard parity on major aspects; wire into CI.
- Add unit tests for edge behaviors: merge window, boundary clamping, retro/station flags, skip conditions.
- Include config validation tests for engine flag and aspect scope mapping.
- Optional: smoke test for compact formatter output with helionext events.
