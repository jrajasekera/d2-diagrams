# Rendering and validation

The skill can author D2 source without any dependencies. Use the D2 CLI for validation, local preview, and exports.

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

### `scripts/check_d2.sh`

Validates one or more `.d2` files by rendering each to a temporary SVG.

```bash
scripts/check_d2.sh templates/system-architecture.d2 tests/smoke.d2
```

Environment variables:

```bash
D2_LAYOUT=elk scripts/check_d2.sh diagram.d2
```

### `scripts/render_d2.sh`

Renders a diagram to a requested path. Output format is inferred from the extension.

```bash
scripts/render_d2.sh diagram.d2 diagram.svg
scripts/render_d2.sh diagram.d2 diagram.pdf
D2_LAYOUT=elk D2_THEME=4 scripts/render_d2.sh diagram.d2 diagram.png
```

### `scripts/scaffold_d2.py`

Lists and copies starter templates.

```bash
scripts/scaffold_d2.py list
scripts/scaffold_d2.py create system-architecture ./architecture.d2
```

## CI validation example

```bash
set -euo pipefail
find docs diagrams -name '*.d2' -print0 | while IFS= read -r -d '' file; do
  scripts/check_d2.sh "$file"
done
```

## Export notes

- SVG is best for web pages and source-controlled documentation.
- SVGs that use Markdown labels rely on browser SVG features; they may not look right in every design tool.
- PNG export uses a browser screenshot pipeline. The first run may need Playwright/browser dependencies.
- PDF export depends on the PNG pipeline and can preserve clickable links.
- PPTX is useful for composition boards and presentation decks.
- GIF and animated SVG work best for short compositions.
- ASCII is useful in terminal docs, but keep the diagram simple and prefer ELK/TALA layouts.

## Validation fallback when CLI is unavailable

Perform a static review:

1. Check braces are balanced.
2. Confirm connections reference keys, not labels.
3. Confirm all style attributes are under `style`.
4. Confirm special object shapes are spelled correctly: `sql_table`, `class`, `sequence_diagram`, `image`, `text`.
5. Check repeated connection references use indexes.
6. Check imports omit or correctly include `.d2`, and relative paths make sense from the importing file.
7. Check that remote icons are acceptable or replace with local paths/no icons.
