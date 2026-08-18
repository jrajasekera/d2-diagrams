#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: scripts/render_d2.sh <input.d2> [output]

Renders D2 source with the d2 CLI. Output format is inferred from the extension
(.svg .png .pdf .pptx .gif .txt). Defaults to <input>.svg.

Layout and theme:
  D2_LAYOUT=elk|dagre|tala      layout engine
  D2_THEME=<id>                 theme id (see: d2 themes)
  D2_DARK_THEME=<id>            theme used when the viewer is in dark mode
  D2_SKETCH=1                   hand-drawn rendering

Composition and geometry:
  D2_PAD=<px>                   padding around the diagram (default 100)
  D2_CENTER=1                   center the diagram in its viewbox
  D2_SCALE=<float>              output scale; 1 disables SVG fit-to-screen
  D2_TARGET=<board>             board to render, e.g. '' or 'layers.x' or 'layers.x.*'
  D2_ANIMATE_INTERVAL=<ms>      package multiple boards as one animated SVG

Text output:
  D2_ASCII_MODE=extended|standard   Unicode box chars, or plain +-| only

Fonts (paths to .ttf files):
  D2_FONT_REGULAR  D2_FONT_ITALIC  D2_FONT_BOLD  D2_FONT_SEMIBOLD  D2_FONT_MONO

Export extras:
  D2_FORCE_APPENDIX=1           add the tooltip/link appendix to SVG too
  D2_OMIT_VERSION=1             omit the D2 version stamp from the image
  D2_WATCH=1                    re-render on change and serve a live preview
EOF
}

if ! command -v d2 >/dev/null 2>&1; then
  echo "error: d2 CLI not found on PATH. Install from https://d2lang.com/tour/install/." >&2
  exit 127
fi

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

input="$1"
if [ ! -f "$input" ]; then
  echo "error: input file not found: $input" >&2
  exit 1
fi

if [ "$#" -eq 2 ]; then
  output="$2"
else
  output="${input%.*}.svg"
fi

args=()

# value flags: --flag=<value> when the variable is non-empty
add_value() { # add_value <flag> <value>
  if [ -n "$2" ]; then
    args+=("$1=$2")
  fi
}

# boolean flags: --flag when the variable is exactly 1
add_bool() { # add_bool <flag> <value>
  if [ "$2" = "1" ]; then
    args+=("$1")
  fi
}

add_value --layout "${D2_LAYOUT:-}"
add_value --theme "${D2_THEME:-}"
add_value --dark-theme "${D2_DARK_THEME:-}"
add_value --pad "${D2_PAD:-}"
add_value --scale "${D2_SCALE:-}"
add_value --animate-interval "${D2_ANIMATE_INTERVAL:-}"
add_value --ascii-mode "${D2_ASCII_MODE:-}"
add_value --font-regular "${D2_FONT_REGULAR:-}"
add_value --font-italic "${D2_FONT_ITALIC:-}"
add_value --font-bold "${D2_FONT_BOLD:-}"
add_value --font-semibold "${D2_FONT_SEMIBOLD:-}"
add_value --font-mono "${D2_FONT_MONO:-}"

# --target accepts the empty string (root board only), so it cannot use
# add_value's non-empty test. Presence of the variable is the signal.
if [ -n "${D2_TARGET+x}" ]; then
  args+=("--target=${D2_TARGET}")
fi

add_bool --sketch "${D2_SKETCH:-0}"
add_bool --center "${D2_CENTER:-0}"
add_bool --force-appendix "${D2_FORCE_APPENDIX:-0}"
add_bool --omit-version "${D2_OMIT_VERSION:-0}"
add_bool --watch "${D2_WATCH:-0}"

d2 ${args[@]+"${args[@]}"} "$input" "$output"
echo "rendered: $output"
