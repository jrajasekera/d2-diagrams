# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not an application** — it is a portable **Agent Skill** package that teaches an agent how to author, convert, validate, and render [D2](https://d2lang.com/) diagrams. The "product" is documentation plus a few helper scripts and templates, shipped as a directory that gets copied into an agent's skills folder (`~/.claude/skills/`, `~/.agents/skills/`, `~/.hermes/skills/`, `~/.pi/agent/skills/`, etc.).

Two distinct modes of work happen here:

- **Using** the skill: producing D2 source for a user. That behavior is fully specified in `SKILL.md` and `references/`.
- **Maintaining** the skill (what you usually do in this repo): editing the docs, templates, scripts, and metadata that make up the package. The notes below are about maintenance.

## Architecture: progressive-disclosure documentation

The package is built around the Agent Skills spec's progressive-disclosure model. Understanding the layering is essential before editing:

- `SKILL.md` is the **single entrypoint**. Its YAML frontmatter (`name`, `description`, `license`, `compatibility`, `metadata`) is what agents load to decide whether to trigger the skill — the `description` is the trigger surface and must list the diagram types, formats, and conversion sources users might ask for. The body is the always-loaded core workflow and syntax.
- `references/*.md` are **on-demand deep docs**, linked from the bottom of `SKILL.md`. They are not loaded until needed. Keep `SKILL.md` lean and push detail down into references:
  - `d2-language-reference.md` — syntax, shapes, styles, layouts, imports, exports
  - `diagram-pattern-cookbook.md` — full recipes per diagram type
  - `conversion-guide.md` — Mermaid/PlantUML/Graphviz/prose → D2
  - `rendering-and-validation.md` — install, CLI, scripts, CI
  - `troubleshooting.md` — common D2 mistakes and repairs
  - `source-notes.md` — research links the skill was authored from
- `templates/*.d2` are copy-ready starter diagrams (one per diagram pattern). `scripts/scaffold_d2.py` enumerates and copies them by file stem.
- `tests/smoke.d2` is the minimal diagram used to prove the toolchain works.

`AGENTS.md` (for agents that read `AGENTS.md` instead of `SKILL.md`) and `agents/openai.yaml` (optional Codex display metadata) are **alternate front-doors to the same content** — they must stay consistent with `SKILL.md`, but `SKILL.md` is canonical.

## Cross-cutting invariants (do not break these)

- **Portability across runtimes.** Content must work for Claude Code, Codex, Hermes, and Pi. Don't introduce runtime-specific assumptions or absolute paths.
- **Relative paths only.** All intra-package links resolve from the package root (e.g. `references/...`, `scripts/check_d2.sh`). The skill is copied to unknown locations.
- **Source is canonical; renders are disposable.** `.gitignore` excludes `*.svg/*.png/*.pdf/*.pptx/*.gif`. Never commit rendered output — it is always regenerable from `.d2` source.
- **The D2 CLI is optional.** Scripts must degrade gracefully when `d2` is absent (exit 127 with a clear message), and the skill must remain useful for source-only authoring. Don't make the CLI a hard dependency.
- **Keep the inventory in sync.** When you add, remove, or rename a file, update `MANIFEST.md` (the file-by-file inventory) and any install/usage examples in `README.md`. When you add a template, no code change is needed for `scaffold_d2.py` (it globs `templates/*.d2`), but mention notable additions in the cookbook.
- **Frontmatter validity.** Changes to `SKILL.md` frontmatter must keep it valid against the Agent Skills spec (https://agentskills.io/specification).

## Commands

Helper scripts live in `scripts/` and assume the D2 CLI is on `PATH` (not installed by default here — install via `curl -fsSL https://d2lang.com/install.sh | sh -s --` or `brew install d2`).

```bash
# Validate one or more diagrams by rendering each to a throwaway SVG (this is the test)
scripts/check_d2.sh tests/smoke.d2
scripts/check_d2.sh templates/*.d2          # validate every template

# Render a diagram; output format inferred from the output extension
scripts/render_d2.sh templates/sequence-diagram.d2 /tmp/out.svg

# Layout/theme overrides are environment variables, not flags
D2_LAYOUT=elk D2_THEME=4 scripts/render_d2.sh templates/system-architecture.d2 /tmp/out.svg
# render_d2.sh also reads: D2_DARK_THEME, D2_SKETCH=1, D2_WATCH=1
# check_d2.sh reads: D2_LAYOUT, D2_THEME

# List / copy starter templates (templates referenced by file stem)
scripts/scaffold_d2.py list
scripts/scaffold_d2.py create sequence-diagram ./login-flow.d2

# Validate the skill package against the Agent Skills spec (requires skills-ref, run from parent dir)
skills-ref validate ./d2-diagrams
```

There is no build step and no test runner beyond `check_d2.sh` (a successful render is the pass condition). After editing any `.d2` template or `SKILL.md`/reference example, validate the affected `.d2` files with `check_d2.sh` if the CLI is available.

## When editing diagram content

The skill's own quality rules (in `SKILL.md`) apply to any `.d2` you write here, especially templates: stable lowercase snake_case IDs distinct from display labels, connect by key not label, semantic containers, labeled high-value edges, and centralized styling via classes/globs/themes/imports. Treat `SKILL.md`'s "Essential D2 syntax" and "Common fixes" sections as the source of truth and keep examples there consistent with `references/d2-language-reference.md`.
