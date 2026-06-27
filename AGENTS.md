# Agent guidance for d2-diagrams

This repository is an Agent Skill. When a user asks for D2 diagrams, diagram-as-code, text-to-diagram conversion, diagram validation/rendering, or D2 troubleshooting, read `SKILL.md` first.

Use relative paths from this folder:

- `references/d2-language-reference.md` for syntax details.
- `references/diagram-pattern-cookbook.md` for diagram recipes.
- `templates/` for starter D2 files.
- `scripts/check_d2.sh` and `scripts/render_d2.sh` when the D2 CLI is available.

Keep generated diagrams maintainable: stable IDs, clear labels, semantic containers, labeled edges, centralized styles, and minimal hard-coded positioning.
