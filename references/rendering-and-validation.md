# Rendering and validation

The skill can author D2 source without any dependencies. Use the D2 CLI for
validation, visual review, local preview, and exports.

**Compiling is not passing.** Everything on this page answers "does D2 accept
this?". Whether the diagram is any good is a separate question, answered by
looking at the render — see
[the layout and medium guide](layout-and-medium-guide.md#the-render--inspect--revise-loop)
and the [visual rubric](visual-design-guide.md#9-visual-rubric).

## Install D2 CLI

Common install approaches:

```bash
# Install script
curl -fsSL https://d2lang.com/install.sh | sh -s --

# macOS Homebrew
brew install d2

# Go install
# Requires a compatible Go toolchain.
go install oss.terrastruct.com/d2@latest
```

Verify:

```bash
d2 version
```

## Checking source

Three different checks, in increasing strength:

```bash
d2 fmt --check diagram.d2   # formatting only
d2 validate diagram.d2      # syntax only - it PARSES, it does not compile
d2 diagram.d2 /tmp/out.svg  # the real check
```

`d2 validate` succeeds on source that fails to render: unresolved keys, indexed
edges that do not exist, missing imports, and unbundlable local icons are all
compile-time failures it does not see. Never treat a `validate` pass as proof the
diagram works. `scripts/check_d2.sh` runs validate first (for the clearer parse
errors) and then a render.

`d2 fmt` rewrites files in place; CI runs `d2 fmt --check`, so run `d2 fmt`
before committing.

## Basic commands

```bash
# SVG is default
d2 diagram.d2

# Explicit outputs
d2 diagram.d2 diagram.svg
d2 diagram.d2 diagram.png
d2 diagram.d2 diagram.pdf
d2 diagram.d2 diagram.pptx
d2 diagram.d2 diagram.gif
d2 diagram.d2 diagram.txt

# Read source from stdin and write SVG to stdout
echo 'x -> y' | d2 - - > diagram.svg
```

## Watch mode

```bash
d2 --watch diagram.d2 diagram.svg
```

Watch mode is useful when iterating with a browser preview.

## Layout and theme

```bash
d2 --layout=elk --theme=4 diagram.d2 diagram.svg
D2_LAYOUT=elk D2_THEME=4 d2 diagram.d2 diagram.svg
```

In-source config:

```d2
vars: {
  d2-config: {
    layout-engine: elk
    theme-id: 4
    dark-theme-id: 200
    pad: 40
    center: true
  }
}
```

CLI flags and environment variables win over source config.

## Helper scripts bundled with this skill

### `scripts/review_d2.py`

The authoring loop. Checks formatting and syntax, renders one candidate per
available layout engine, reports each candidate's dimensions, aspect ratio, and
type sizes, and writes an HTML contact sheet showing them side by side.

```bash
scripts/review_d2.py diagram.d2
scripts/review_d2.py diagram.d2 --dark --png
scripts/review_d2.py a.d2 b.d2 --engines elk,dagre --out-dir ./review --open
```

- `--dark` renders a dark variant per engine, and warns when the dark render
  reuses the light palette — the signature of explicit fills overriding the
  theme.
- `--png` writes images as well as SVGs, which is what an agent needs in order to
  *see* the diagram. It uses D2's PNG export when that works and falls back to a
  headless-browser screenshot of the SVG when it does not.
- Output goes to a temporary directory unless `--out-dir` says otherwise.

The reported numbers map onto the rubric: aspect ratio and pixel width tell you
whether the diagram fits its destination, and the smallest `font-size` tells you
whether anything is going to be unreadable.

### `scripts/check_d2.sh`

Validates syntax and then compiles each file to a temporary SVG.

```bash
scripts/check_d2.sh templates/system-architecture.d2 tests/smoke.d2
D2_LAYOUT=elk scripts/check_d2.sh diagram.d2
D2_FMT=1 scripts/check_d2.sh diagram.d2      # also require d2 fmt --check
```

### `scripts/render_d2.sh`

Renders a diagram to a requested path. Output format is inferred from the
extension. Every override is an environment variable rather than a flag:

```bash
scripts/render_d2.sh diagram.d2 diagram.svg
D2_LAYOUT=elk D2_THEME=4 scripts/render_d2.sh diagram.d2 diagram.png

# True-size render, for judging type at the destination size
D2_SCALE=1 scripts/render_d2.sh diagram.d2 diagram.svg

# One board out of a composition
D2_TARGET='layers.deployment' scripts/render_d2.sh diagram.d2 deployment.svg

# All boards as one animated SVG
D2_ANIMATE_INTERVAL=1600 scripts/render_d2.sh diagram.d2 walkthrough.svg

# Print: materialize tooltips and links as an appendix, drop the version stamp
D2_FORCE_APPENDIX=1 D2_OMIT_VERSION=1 scripts/render_d2.sh diagram.d2 diagram.pdf

# Brand fonts
D2_FONT_REGULAR=./fonts/Inter-Regular.ttf D2_FONT_BOLD=./fonts/Inter-Bold.ttf \
  scripts/render_d2.sh diagram.d2 diagram.svg
```

Run `scripts/render_d2.sh` with no arguments for the full variable list.

### `scripts/scaffold_d2.py`

Lists templates and style packs, and creates a diagram from a template wired to a
style pack. The pack (and everything it imports) is copied next to the output, so
the new diagram does not depend on where this skill is installed.

```bash
scripts/scaffold_d2.py list
scripts/scaffold_d2.py styles
scripts/scaffold_d2.py create system-architecture ./architecture.d2
scripts/scaffold_d2.py create system-architecture ./deck.d2 --medium slides
scripts/scaffold_d2.py create event-driven ./post.d2 --style editorial
```

### `scripts/validate_docs.py`

Compiles every fenced ```` ```d2 ```` example in the package's Markdown, so a
snippet that stopped being valid D2 fails here rather than in a user's editor.
Skip a block with `<!-- validate:skip -->` on the preceding line — for deliberate
counter-examples and for fragments that cannot stand alone.

```bash
scripts/validate_docs.py
scripts/validate_docs.py --list
```

### `scripts/render_gallery.sh`

Regenerates the committed `gallery/**/preview.svg` files, or checks them for
drift. Multi-board diagrams are rendered as one animated SVG.

```bash
scripts/render_gallery.sh
scripts/render_gallery.sh --check
```

`--check` is a cheap visual regression test. A failure is information, not
automatically a bug: renderer versions differ. Look at the new image before
deciding whether it is better or worse.

## CI

`.github/workflows/validate.yml` runs the whole suite: formatting, validate and
compile over every `.d2`, the documentation examples, every template under both
layout engines, gallery preview drift, and a scaffold round-trip.

**Pin the D2 version in CI.** Layout output changes between releases, so an
unpinned CLI makes committed previews drift for reasons unrelated to any change
in the repo. Bump the pin deliberately, regenerate the previews in the same
commit, and look at what changed.

For a project of your own that just needs its diagrams checked:

```bash
set -euo pipefail
find docs diagrams -name '*.d2' -print0 | while IFS= read -r -d '' file; do
  scripts/check_d2.sh "$file"
done
```

## Export notes

- SVG is best for web pages and source-controlled documentation.
- **SVG fits to its container by default.** A wide diagram previewed in a browser
  shows uniformly small text even when the type is 26px. Render with `--scale 1`
  (`D2_SCALE=1`) before concluding anything about legibility, and check the
  `viewBox` width against the column the diagram will actually occupy.
- SVGs that use Markdown labels rely on browser SVG features; they may not look
  right in every design tool.
- PNG export uses a browser screenshot pipeline that **downloads a Playwright
  browser on first use**. In sandboxes, offline CI, and restricted networks this
  fails with a 404 or a timeout and no PNG is produced. Render SVG and screenshot
  it with a local headless browser instead — `scripts/review_d2.py --png` does
  this automatically.
- PDF and PPTX export depend on the same pipeline and fail the same way. PDF
  preserves clickable links; `--force-appendix` materializes tooltips and links
  for formats that cannot show them.
- PPTX puts one board per slide, which is the right export for a composition
  used as a deck.
- GIF and animated SVG (`--animate-interval`) work best for short compositions.
- ASCII (`d2 in.d2 out.txt`) is useful in terminal docs. `--ascii-mode=extended`
  (the default) uses Unicode box characters; `--ascii-mode=standard` restricts to
  `+-|`. Keep the diagram simple, prefer ELK or TALA, and remember that color,
  dashes, shadows, and icons carry no meaning there. It is still marked beta
  upstream, so a poor result is a reason to simplify the diagram.

## Validation fallback when CLI is unavailable

Perform a static review, then **say that is what you did**: report the diagram as
*statically reviewed but not visually verified*. Do not present a static pass as a
design verdict.

Checks:

1. Check braces are balanced.
2. Confirm connections reference keys, not labels.
3. Confirm all style attributes are under `style`.
4. Confirm special object shapes are spelled correctly: `sql_table`, `class`, `sequence_diagram`, `image`, `text`.
5. Check repeated connection references use indexes.
6. Check imports omit or correctly include `.d2`, and relative paths make sense from the importing file.
7. Check that remote icons are acceptable or replace with local paths/no icons.
