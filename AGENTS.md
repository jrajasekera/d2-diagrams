# Agent Guidance For d2-diagrams

This repository is a portable Agent Skill package for creating, converting,
validating, rendering, and troubleshooting D2 diagrams. It is documentation,
templates, metadata, and a few helper scripts, not an application.

When a user asks for D2 diagrams, diagram-as-code, text-to-diagram conversion,
diagram validation/rendering, or D2 troubleshooting, read `SKILL.md` first.
`SKILL.md` is the canonical skill entrypoint; this file is always-on repository
guidance for agents maintaining the package.

## Repository Model

The skill uses progressive-disclosure documentation:

- `SKILL.md` is the primary entrypoint and trigger surface. Keep it concise and
  useful when loaded on every skill invocation.
- `references/*.md` holds deeper material loaded only when needed:
  - `references/d2-language-reference.md` for syntax, shapes, styles, imports,
    layout, and export details.
  - `references/diagram-pattern-cookbook.md` for practical diagram recipes.
  - `references/conversion-guide.md` for Mermaid, PlantUML, Graphviz, and prose
    conversion guidance.
  - `references/rendering-and-validation.md` for D2 CLI usage, helper scripts,
    and CI examples.
  - `references/troubleshooting.md` for common mistakes and fixes.
  - `references/source-notes.md` for research links.
- `templates/*.d2` contains copy-ready starter diagrams. Template names are used
  by `scripts/scaffold_d2.py`.
- `tests/smoke.d2` is the smallest validation target for the render toolchain.
- `MANIFEST.md`, `README.md`, `CLAUDE.md`, and `agents/openai.yaml` are package
  metadata or alternate front doors. Keep them consistent with `SKILL.md`.

## Maintenance Rules

- Preserve portability across Claude Code, Codex, Hermes Agent, Pi, and other
  Agent Skills-compatible runtimes. Avoid runtime-specific assumptions.
- Use relative paths from the package root. The skill may be copied to any
  location under a user's skill directory.
- Treat D2 source as canonical. Rendered files such as SVG, PNG, PDF, PPTX, and
  GIF are disposable outputs and should not be committed.
- Keep the D2 CLI optional. The skill must remain useful for source-only diagram
  authoring, and helper scripts should fail clearly when `d2` is unavailable.
- When adding, removing, or renaming package files, update `MANIFEST.md` and any
  affected `README.md` examples.
- When changing `SKILL.md` frontmatter, preserve Agent Skills spec validity.

## Diagram Quality

For `.d2` source and examples, prefer maintainable diagrams over hard-coded
positioning:

- Use stable lowercase snake_case IDs that are distinct from display labels.
- Connect nodes by key, not label.
- Group related objects with semantic containers.
- Label edges when the relationship is not obvious.
- Centralize repeated styling with classes, globs, themes, or imports.
- Keep manual positioning minimal unless the diagram requires a specific spatial
  story.

## Useful Commands

```bash
# Validate one or more diagrams by rendering to temporary SVG files.
scripts/check_d2.sh tests/smoke.d2
scripts/check_d2.sh templates/*.d2

# Render a diagram. The output format is inferred from the extension.
scripts/render_d2.sh templates/sequence-diagram.d2 /tmp/sequence.svg

# Use layout/theme overrides.
D2_LAYOUT=elk D2_THEME=4 scripts/render_d2.sh templates/system-architecture.d2 /tmp/system.svg

# List and copy starter templates.
scripts/scaffold_d2.py list
scripts/scaffold_d2.py create sequence-diagram ./login-flow.d2
```

If the D2 CLI is unavailable and only documentation changed, use static review
plus `git diff --check`. If `.d2` files changed and `d2` is available, validate
the affected diagrams with `scripts/check_d2.sh`.
