# d2-diagrams Agent Skill

A portable Agent Skills package that teaches an agent to **design** [D2](https://d2lang.com/) diagrams — not merely to emit D2 that compiles.

This README is organized by what you came to do: understand the package, install it for the first time, perform specific tasks, or look up exact facts.

- [What this is](#what-this-is) — orientation, if you are deciding whether to use it.
- [Get started](#get-started) — install it into Claude Code and confirm it works.
- [How-to guides](#how-to-guides) — install into other runtimes, add the CLI, review, render, scaffold.
- [Reference](#reference) — install locations, scripts, environment variables, package contents.
- [Learn more](#learn-more) — the skill's own documentation and design notes.

## What this is

`d2-diagrams` is **not an application**. It is an Agent Skill: a directory of documentation, templates, and helper scripts that an agent loads to produce good D2 diagrams. You install it by copying it into your agent's skills folder; your agent reads it on demand.

It targets any runtime that implements the Agent Skills / `SKILL.md` convention — Claude Code, OpenAI Codex, Hermes Agent, and Pi.

Three ideas shape the package and explain most of its behavior:

- **A successful render is not a quality gate.** D2 will happily draw unreadable 8px labels, forty crossing edges, and a 4000px-wide strip. So the skill's core loop is *render candidates → look at the image → revise*, scored against a visual rubric. `scripts/review_d2.py` exists to make that loop cheap, and the [gallery](gallery/) shows what the finished result should look like.
- **The D2 CLI is optional.** The skill helps an agent write correct `.d2` source with no tools installed. The CLI adds local validation, rendering, and the visual-review loop. Helper scripts degrade gracefully when `d2` is absent, and the skill says so rather than claiming a diagram was visually verified when it was not.
- **Source is canonical; renders are disposable.** Diagrams live as `.d2` text and are regenerated as needed, so rendered files are not tracked — with one deliberate exception, the committed `gallery/**/preview.svg` reference images.

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

### Review a diagram visually

This is the loop the skill is built around. `review_d2.py` checks formatting and syntax, renders one candidate per available layout engine, reports each candidate's dimensions, aspect ratio, and type sizes, and writes an HTML contact sheet showing them side by side:

```bash
scripts/review_d2.py my-diagram.d2 --dark --png
```

Open the contact sheet it prints, compare the candidates at the size the diagram will actually be used at, and revise. `--png` also writes images, which is what an agent needs in order to see the diagram at all; it falls back to a headless-browser screenshot when D2's own PNG pipeline is unavailable.

Then score the result against the visual rubric in [`references/visual-design-guide.md`](references/visual-design-guide.md).

### Validate diagrams

Validation runs `d2 validate` for syntax, then renders each file to a throwaway SVG, and reports `ok` or `failed` per file:

```bash
scripts/check_d2.sh tests/smoke.d2
scripts/check_d2.sh $(git ls-files '*.d2')   # everything
D2_FMT=1 scripts/check_d2.sh templates/*.d2  # also require d2 fmt
```

This answers "does it compile", not "is it any good" — use `review_d2.py` for the latter. To validate with a specific layout or theme, set the relevant [environment variables](#environment-variables).

To compile the fenced `d2` examples inside the Markdown, which is how documentation drift gets caught:

```bash
scripts/validate_docs.py
```

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

List the bundled starter diagrams and style packs, then create a diagram:

```bash
scripts/scaffold_d2.py list
scripts/scaffold_d2.py styles
scripts/scaffold_d2.py create sequence-diagram ./login-flow.d2
```

`create` copies the template **and the style pack it uses** into a `styles/` directory beside the output, so the new diagram does not depend on where this skill is installed. Pick a different look with `--style`, or let the destination choose one with `--medium`:

```bash
scripts/scaffold_d2.py create system-architecture ./deck.d2 --medium slides
scripts/scaffold_d2.py create event-driven ./post.d2 --style editorial
```

`create` refuses to overwrite an existing file unless you pass `--force`. The full sets are in [Templates](#templates) and [Style packs](#style-packs).

### Restyle a diagram

Diagrams import a style pack instead of hand-coloring shapes:

```d2
...@styles/minimal-light

api: API Service {class: primary_service}
db: PostgreSQL {class: datastore}
api -> db: SQL {class: primary_edge}
```

Changing the whole look means changing that one import line. See [Style packs](#style-packs) for the list, and the [visual design guide](references/visual-design-guide.md) for the system behind them.

### Regenerate the gallery previews

`gallery/**/preview.svg` is committed on purpose. After changing a gallery diagram or a style pack:

```bash
scripts/render_gallery.sh          # rewrite them
scripts/render_gallery.sh --check  # fail if any is out of date
```

`--check` doubles as a cheap visual regression test: if a D2 upgrade or a style-pack edit changes a reference diagram, it says so. Look at the new image before deciding whether that is an improvement or a regression.

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
| `scripts/review_d2.py` | Render one candidate per layout engine, report geometry and type sizes, write an HTML contact sheet. `--dark` adds dark variants, `--png` writes images for inspection. | `scripts/review_d2.py in.d2 --png` |
| `scripts/check_d2.sh` | Validate syntax (`d2 validate`) then compile each `.d2` to a temporary SVG. Prints `ok`/`failed` per file; non-zero exit if any fail. | `scripts/check_d2.sh tests/smoke.d2` |
| `scripts/render_d2.sh` | Render `<input.d2>` to `[output]` (format inferred from extension; defaults to `<input>.svg`). | `scripts/render_d2.sh in.d2 out.png` |
| `scripts/scaffold_d2.py` | `list` templates, `styles` for packs and mediums, `create <template> <output> [--style] [--medium] [--force]`. | `scripts/scaffold_d2.py create grid-diagram ./matrix.d2` |
| `scripts/validate_docs.py` | Compile every fenced ```` ```d2 ```` example in the package's Markdown. | `scripts/validate_docs.py` |
| `scripts/render_gallery.sh` | Regenerate the committed gallery previews, or `--check` them for drift. | `scripts/render_gallery.sh --check` |

### Environment variables

Both scripts read overrides from the environment rather than flags. Unset variables are ignored.

| Variable | Used by | Values | Effect |
|---|---|---|---|
| `D2_LAYOUT` | `check_d2.sh`, `render_d2.sh` | `dagre`, `elk`, `tala` | Layout engine (`--layout`). |
| `D2_THEME` | `check_d2.sh`, `render_d2.sh` | theme id | Color theme (`--theme`). |
| `D2_FMT` | `check_d2.sh` | `1` | Also require `d2 fmt --check` to pass. |
| `D2_DARK_THEME` | `render_d2.sh` | dark theme id | Dark-mode theme (`--dark-theme`). |
| `D2_SKETCH` | `render_d2.sh` | `1` | Hand-drawn sketch style (`--sketch`). |
| `D2_WATCH` | `render_d2.sh` | `1` | Re-render on change (`--watch`). |
| `D2_PAD` | `render_d2.sh` | pixels | Padding around the diagram (`--pad`, default 100). |
| `D2_CENTER` | `render_d2.sh` | `1` | Center in the viewbox (`--center`). |
| `D2_SCALE` | `render_d2.sh` | float | Output scale (`--scale`); `1` disables SVG fit-to-screen. |
| `D2_TARGET` | `render_d2.sh` | board path | Board to render (`--target`), e.g. `layers.deployment` or `''` for root. |
| `D2_ANIMATE_INTERVAL` | `render_d2.sh` | milliseconds | Package multiple boards as one animated SVG (`--animate-interval`). |
| `D2_ASCII_MODE` | `render_d2.sh` | `extended`, `standard` | Unicode box characters, or plain `+-\|` (`--ascii-mode`). |
| `D2_FORCE_APPENDIX` | `render_d2.sh` | `1` | Add the tooltip/link appendix to SVG too (`--force-appendix`). |
| `D2_OMIT_VERSION` | `render_d2.sh` | `1` | Omit the D2 version stamp (`--omit-version`). |
| `D2_FONT_REGULAR` etc. | `render_d2.sh` | path to `.ttf` | Custom fonts; also `D2_FONT_ITALIC`, `D2_FONT_BOLD`, `D2_FONT_SEMIBOLD`, `D2_FONT_MONO`. |

### Templates

Starter `.d2` files in `templates/`, referenced by file stem. Copy one with `scripts/scaffold_d2.py create <name> <output>`.

`ci-cd-pipeline`, `cloud-network`, `composition-scenarios`, `erd-sql-tables`, `event-driven`, `grid-diagram`, `import-common-style`, `import-example`, `markdown-latex-code`, `sequence-diagram`, `styles-and-classes`, `system-architecture`, `uml-classes`

### Style packs

Importable visual systems in `styles/`, referenced by file stem. Each spreads `semantic-classes` and adds a palette.

| Pack | Best for |
|---|---|
| `semantic-classes` | Light/dark **adaptive** diagrams — structure only, no colors, so the theme supplies the palette. Also the base of every other pack. |
| `minimal-light` | READMEs, design docs, wikis, PRs. |
| `minimal-dark` | Destinations known to be dark. Not adaptive. |
| `presentation` | Slides: one type tier larger, heavier strokes, wider padding. |
| `editorial` | Blog posts and long-form writing. |
| `sketch` | Proposals and drafts, hand-drawn. |

`--medium` maps a destination to a default pack: `docs`, `adaptive`, `dark`, `slides`, `print`, `editorial`, `sketch`, `terminal`. Run `scripts/scaffold_d2.py styles` for the current list.

All packs provide the same classes: `actor`, `external_system`, `boundary`, `primary_service`, `secondary_service`, `datastore`, `queue`, `decision`, `annotation`, `success`, `warning`, `failure`, `primary_edge`, `secondary_edge`, `async_edge`, `fallback_edge`.

### Package contents

```text
d2-diagrams/
├── SKILL.md            # Main skill instructions and trigger metadata (canonical)
├── AGENTS.md           # Same content for agents that read AGENTS.md
├── MANIFEST.md         # File-by-file inventory of the package
├── README.md           # This file
├── LICENSE             # MIT license
├── references/         # On-demand deep reference docs
├── styles/             # Semantic class vocabulary and style packs
├── templates/          # Starter D2 templates
├── gallery/            # Finished diagrams + design notes + committed previews
├── scripts/            # Review, validation, rendering, scaffolding helpers
├── tests/              # Smoke test and per-style-pack probes
├── .github/workflows/  # CI: formatting, compilation, doc examples, preview drift
└── agents/openai.yaml  # Optional Codex display metadata
```

[`MANIFEST.md`](MANIFEST.md) is the authoritative file-by-file inventory.

## Learn more

- [`SKILL.md`](SKILL.md) — the skill itself: the design workflow, visual rules, D2 syntax, diagram patterns, and the quality bar the agent applies.
- [`gallery/`](gallery/) — finished diagrams with the reasoning behind them, including a [before/after pair](gallery/architecture-minimal/) showing valid-but-bad D2 next to the designed version.
- [`references/visual-design-guide.md`](references/visual-design-guide.md) — hierarchy, typography, color, edge hierarchy, density, icons, legends, and the visual rubric.
- [`references/layout-and-medium-guide.md`](references/layout-and-medium-guide.md) — the render/inspect/revise loop, layout-engine selection, and output-medium profiles.
- [`references/`](references/) — the rest of the deep docs: language reference, pattern cookbook, conversion guide, rendering/validation, troubleshooting, and source notes.
- [`MANIFEST.md`](MANIFEST.md) — full package inventory.
- [`CLAUDE.md`](CLAUDE.md) — maintenance guidance and the design invariants behind the package.
- [Agent Skills specification](https://agentskills.io/specification) — the standard this package targets.

## License

MIT. See [`LICENSE`](LICENSE).
