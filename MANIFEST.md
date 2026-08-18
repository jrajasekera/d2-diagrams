# Manifest

## Entrypoints

- `SKILL.md` — primary Agent Skills entrypoint (canonical).
- `AGENTS.md` — always-on guidance for agents maintaining this repository.
- `agents/openai.yaml` — optional Codex/plugin display metadata.
- `README.md` — installation and usage instructions.
- `CLAUDE.md` — maintenance guidance and package design invariants.
- `MANIFEST.md` — this inventory.
- `LICENSE` — MIT license.
- `.gitignore` — excludes rendered outputs, except `gallery/**/preview.svg`.

## References (loaded on demand)

- `references/visual-design-guide.md` — thesis, hierarchy, typography, color,
  edge hierarchy, density, icons, legends, and the visual rubric.
- `references/layout-and-medium-guide.md` — the render/inspect/revise loop,
  layout-engine selection, output-medium profiles, multi-board storytelling.
- `references/d2-language-reference.md` — compact D2 syntax reference.
- `references/diagram-pattern-cookbook.md` — practical diagram recipes.
- `references/conversion-guide.md` — Mermaid/PlantUML/Graphviz/prose conversion.
- `references/rendering-and-validation.md` — CLI and helper script guidance.
- `references/troubleshooting.md` — common mistakes and fixes.
- `references/source-notes.md` — research links.

## Styles

The visual system. Every pack spreads `semantic-classes` and adds a palette.

- `styles/semantic-classes.d2` — the class vocabulary, structure only, no colors.
- `styles/minimal-light.d2` — documentation default.
- `styles/minimal-dark.d2` — known-dark destinations.
- `styles/presentation.d2` — slides.
- `styles/editorial.d2` — long-form writing.
- `styles/sketch.d2` — hand-drawn drafts.

## Templates

Starter `.d2` files, referenced by file stem by `scripts/scaffold_d2.py`.

- `templates/system-architecture.d2`
- `templates/cloud-network.d2`
- `templates/ci-cd-pipeline.d2`
- `templates/event-driven.d2`
- `templates/sequence-diagram.d2`
- `templates/erd-sql-tables.d2`
- `templates/uml-classes.d2`
- `templates/grid-diagram.d2`
- `templates/composition-scenarios.d2`
- `templates/markdown-latex-code.d2`
- `templates/styles-and-classes.d2`
- `templates/import-common-style.d2`, `templates/import-example.d2`

## Gallery

Finished diagrams with design notes. Each directory holds `diagram.d2`,
`preview.svg` (committed on purpose), and `design-notes.md`.

- `gallery/README.md` — index and reading guide.
- `gallery/architecture-minimal/` — includes `before.d2`, the before/after pair.
- `gallery/architecture-dark/` — light/dark adaptive.
- `gallery/ci-cd-presentation/` — designed for a projector.
- `gallery/event-driven-editorial/` — designed for prose.
- `gallery/incident-failover/` — a runbook told in `steps`.
- `gallery/sequence-authentication/` — one flow, no branches.
- `gallery/erd-domain-focused/` — five tables out of sixty.
- `gallery/cloud-network/` — a diagram that has to prove something.

## Scripts

- `scripts/review_d2.py` — render layout-engine candidates, report geometry and
  type sizes, write an HTML contact sheet; `--png` for image inspection.
- `scripts/check_d2.sh` — validate syntax and compile each file.
- `scripts/render_d2.sh` — render to a requested format with `D2_*` overrides.
- `scripts/scaffold_d2.py` — list templates and style packs; create a diagram
  from a template wired to a style pack.
- `scripts/validate_docs.py` — compile every fenced `d2` example in the Markdown.
- `scripts/render_gallery.sh` — regenerate or drift-check the gallery previews.

## Tests

- `tests/smoke.d2` — smallest validation target for the render toolchain.
- `tests/fixtures/probe-*.d2` — one probe per style pack, exercising every
  semantic class.

## CI

- `.github/workflows/validate.yml` — pinned D2 version; runs the script suite.
