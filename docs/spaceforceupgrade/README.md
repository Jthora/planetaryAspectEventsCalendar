# Space Force Interpretation Upgrade

This folder anchors the new interpretation mode that speaks to Space Force mission life. It outlines the intent, scope, personas, and success criteria so engineering and content threads stay aligned.

## Mission
- Deliver an `--interpretation-mode space_force` option that reframes planetary aspects for Guardians, mission planners, and support crews.
- Keep outputs battle-rhythm ready: concise briefs, clear risk posture, and actionable next steps for orbital, cyber, and comms operations.
- Preserve backward compatibility with the `standard` and `business` personas while sharing as much infrastructure as possible.

## Document Map
| File | Purpose |
| --- | --- |
| `README.md` | High-level overview + entry point. |
| `style-guide.md` | Editorial voice, terminology, and copy blocks for the Space Force persona. |
| `dictionary-blueprint.md` | Data contracts plus required keys for aspect/planet guidance. |
| `implementation-roadmap.md` | Engineering tasks, sequencing, and dependencies. |
| `qa-checklist.md` | Verification steps, test coverage expectations, and sign-off rubric. |

## Guiding Principles
1. **Operational Relevance** – Copy should mirror mission briefs (status, intent, execution, assessment).
2. **Modularity** – Dictionaries stay decoupled so new personas can plug in with minimal code changes.
3. **Validation First** – Every new narrative path ships with automated completeness checks and sample ICS exports.
4. **Security Awareness** – No classified references; keep guidance high-level but tactically useful.

## Key Stakeholders
- **Content**: Space Force veterans + editorial partners crafting authentic tone.
- **Engineering**: Daily transit pipeline owners implementing the new mode.
- **QA**: Multi-mode reviewers verifying ICS output, tests, and validation scripts.

## Validation & Samples
- Run `python tools/validate_spaceforce_dicts.py --strict` before merging to ensure the dictionaries match the schema outlined in `dictionary-blueprint.md`.
- Latest sample export: `output/sample_space_force_2025-01-01_to_2025-01-03.ics` (generated with `--daily-summary`, `--lunar-phases`, and `--interpretation-mode space_force`).
