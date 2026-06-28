# d2-diagrams Agent Skill

A portable Agent Skills package that teaches an agent to create, edit, convert, validate, and render [D2](https://d2lang.com/) diagrams.

This README is organized by what you came to do: understand the package, install it for the first time, perform specific tasks, or look up exact facts.

- [What this is](#what-this-is) — orientation, if you are deciding whether to use it.
- [Get started](#get-started) — install it into Claude Code and confirm it works.
- [How-to guides](#how-to-guides) — install into other runtimes, add the CLI, validate, render, scaffold.
- [Reference](#reference) — install locations, scripts, environment variables, package contents.
- [Learn more](#learn-more) — the skill's own documentation and design notes.

## What this is

`d2-diagrams` is **not an application**. It is an Agent Skill: a directory of documentation, templates, and helper scripts that an agent loads to produce good D2 diagrams. You install it by copying it into your agent's skills folder; your agent reads it on demand.

It targets any runtime that implements the Agent Skills / `SKILL.md` convention — Claude Code, OpenAI Codex, Hermes Agent, and Pi.

Two ideas shape the package and explain most of its behavior:

- **The D2 CLI is optional.** The skill helps an agent write correct `.d2` source with no tools installed. The CLI only adds local validation and rendering to images. Helper scripts degrade gracefully when `d2` is absent.
- **Source is canonical; renders are disposable.** Diagrams live as `.d2` text and are regenerated as needed, so rendered files are not tracked.

For the full picture of what the skill does once installed, read [`SKILL.md`](SKILL.md). For why the package is shaped this way, see [`CLAUDE.md`](CLAUDE.md).

## Get started

This installs the skill into Claude Code and confirms your agent can use it. We will copy the package into your user skills directory, check the entrypoint landed, and ask the agent for a diagram. You do **not** need the D2 CLI for any of this.

Using Codex, Hermes, or Pi instead? See [Install into another runtime](#install-into-another-runtime).

1. Copy the package into your Claude Code user skills directory:

   ```bash
   mkdir -p ~/.claude/skills
   cp -R d2-diagrams ~/.claude/skills/
   ```

2. Confirm the entrypoint is in place:

   ```bash
   ls ~/.claude/skills/d2-diagrams/SKILL.md
   ```

   The command should print the path back. If you see `No such file or directory`, re-run the copy step from the directory that contains `d2-diagrams`.

3. Start (or restart) Claude Code and ask for a diagram, for example:

   > Create a D2 sequence diagram for a login flow.

   The agent loads the skill and replies with `.d2` source. That is the whole loop: the skill is installed and triggering.

When you want local validation and rendered images, continue with [Install the D2 CLI](#install-the-d2-cli).

## How-to guides

Task-focused directions for readers who already know the basics. Each guide links to [Reference](#reference) for exhaustive options instead of repeating them.

### Install into another runtime

Copy the `d2-diagrams` folder into the skills directory your agent scans. The directories differ per runtime; the copy step is the same.

```bash
# OpenAI Codex (user-level)
mkdir -p ~/.agents/skills && cp -R d2-diagrams ~/.agents/skills/

# Hermes Agent
mkdir -p ~/.hermes/skills && cp -R d2-diagrams ~/.hermes/skills/

# Pi (user-level)
mkdir -p ~/.pi/agent/skills && cp -R d2-diagrams ~/.pi/agent/skills/
```

Project-level installs and Pi's `.agents/skills` fallback are listed in [Install locations](#install-locations).

### Install the D2 CLI

Install the CLI when you want the helper scripts to validate or render locally. The recommended installer:

```bash
curl -fsSL https://d2lang.com/install.sh | sh -s --
d2 version
```

Homebrew (`brew install d2`), Go (`go install oss.terrastruct.com/d2@latest`), release binaries, Windows installers, and Docker also work. If a script reports `d2 CLI not found on PATH`, the CLI is not installed or not on your `PATH` — the skill still works for source-only authoring.

### Validate diagrams

Validation renders each file to a throwaway SVG and reports `ok` or `failed` per file. Run it from the skill root after editing any `.d2`:

```bash
scripts/check_d2.sh tests/smoke.d2
scripts/check_d2.sh templates/*.d2        # validate every template
```

A successful render is the pass condition; there is no separate test runner. To validate with a specific layout or theme, set the relevant [environment variables](#environment-variables).

### Render a diagram

Render to a file whose format is inferred from its extension (`.svg`, `.png`, `.pdf`, `.pptx`, `.gif`, `.txt`):

```bash
scripts/render_d2.sh templates/sequence-diagram.d2 ./login-flow.svg
```

Omit the output path to render next to the input as `<name>.svg`. Override layout, theme, sketch, or watch mode with [environment variables](#environment-variables):

```bash
D2_LAYOUT=elk D2_THEME=4 scripts/render_d2.sh templates/system-architecture.d2 ./system.svg
```

> PNG, PDF, PPTX, and GIF exports may need extra browser/Playwright dependencies for the D2 CLI.

### Start from a template

List the bundled starter diagrams, then copy one to a new file to edit:

```bash
scripts/scaffold_d2.py list
scripts/scaffold_d2.py create sequence-diagram ./login-flow.d2
```

`create` refuses to overwrite an existing file unless you pass `--force`. The full set of template names is in [Templates](#templates).

### Validate the skill package

If you maintain this package, confirm it still conforms to the [Agent Skills specification](https://agentskills.io/specification). Run the reference validator from the directory that contains `d2-diagrams`:

```bash
skills-ref validate ./d2-diagrams
```

This checks `SKILL.md` frontmatter and naming conventions. It requires the `skills-ref` tool, which is separate from the D2 CLI.

## Reference

Exact facts about install locations, scripts, environment variables, and package contents.

### Install locations

| Runtime | User-level | Project-level |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` | `.agents/skills/` |
| Hermes Agent | `~/.hermes/skills/` | — |
| Pi | `~/.pi/agent/skills/` | `.pi/skills/` |

Pi also scans compatible `.agents/skills` directories, so the Codex locations work for Pi as well. Install by copying the `d2-diagrams` folder into the chosen directory.

### Scripts

Helper scripts live in `scripts/` and assume the D2 CLI is on `PATH`. Each exits with status `127` and a clear message when `d2` is absent.

| Script | Purpose | Example |
|---|---|---|
| `scripts/check_d2.sh` | Validate one or more `.d2` files by rendering each to a temporary SVG. Prints `ok`/`failed` per file; non-zero exit if any fail. | `scripts/check_d2.sh tests/smoke.d2` |
| `scripts/render_d2.sh` | Render `<input.d2>` to `[output]` (format inferred from extension; defaults to `<input>.svg`). | `scripts/render_d2.sh in.d2 out.png` |
| `scripts/scaffold_d2.py` | `list` available templates, or `create <template> <output> [--force]` to copy one. | `scripts/scaffold_d2.py create grid-diagram ./matrix.d2` |

### Environment variables

Both scripts read overrides from the environment rather than flags. Unset variables are ignored.

| Variable | Used by | Values | Effect |
|---|---|---|---|
| `D2_LAYOUT` | `check_d2.sh`, `render_d2.sh` | `dagre`, `elk`, `tala` | Layout engine (`--layout`). |
| `D2_THEME` | `check_d2.sh`, `render_d2.sh` | theme id | Color theme (`--theme`). |
| `D2_DARK_THEME` | `render_d2.sh` | dark theme id | Dark-mode theme (`--dark-theme`). |
| `D2_SKETCH` | `render_d2.sh` | `1` | Hand-drawn sketch style (`--sketch`). |
| `D2_WATCH` | `render_d2.sh` | `1` | Re-render on change (`--watch`). |

### Templates

Starter `.d2` files in `templates/`, referenced by file stem. Copy one with `scripts/scaffold_d2.py create <name> <output>`.

`ci-cd-pipeline`, `cloud-network`, `composition-scenarios`, `erd-sql-tables`, `grid-diagram`, `import-common-style`, `import-example`, `markdown-latex-code`, `sequence-diagram`, `styles-and-classes`, `system-architecture`, `uml-classes`

### Package contents

```text
d2-diagrams/
├── SKILL.md            # Main skill instructions and trigger metadata (canonical)
├── AGENTS.md           # Same content for agents that read AGENTS.md
├── MANIFEST.md         # File-by-file inventory of the package
├── README.md           # This file
├── LICENSE             # MIT license
├── references/         # On-demand deep reference docs
├── templates/          # Starter D2 templates
├── scripts/            # Optional validation/rendering/scaffolding helpers
├── tests/              # Smoke-test D2 source
└── agents/openai.yaml  # Optional Codex display metadata
```

[`MANIFEST.md`](MANIFEST.md) is the authoritative file-by-file inventory.

## Learn more

- [`SKILL.md`](SKILL.md) — the skill itself: workflow, D2 syntax, diagram patterns, and quality rules the agent applies.
- [`references/`](references/) — deep docs the skill loads on demand: language reference, pattern cookbook, conversion guide, rendering/validation, troubleshooting, and source notes.
- [`MANIFEST.md`](MANIFEST.md) — full package inventory.
- [`CLAUDE.md`](CLAUDE.md) — maintenance guidance and the design invariants behind the package.
- [Agent Skills specification](https://agentskills.io/specification) — the standard this package targets.

## License

MIT. See [`LICENSE`](LICENSE).
