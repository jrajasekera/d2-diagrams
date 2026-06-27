#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: scripts/render_d2.sh <input.d2> [output]

Renders D2 source with the d2 CLI. Output format is inferred from extension.
Environment overrides:
  D2_LAYOUT=elk|dagre|tala
  D2_THEME=<theme-id>
  D2_DARK_THEME=<dark-theme-id>
  D2_SKETCH=1
  D2_WATCH=1
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
if [ -n "${D2_LAYOUT:-}" ]; then
  args+=("--layout=${D2_LAYOUT}")
fi
if [ -n "${D2_THEME:-}" ]; then
  args+=("--theme=${D2_THEME}")
fi
if [ -n "${D2_DARK_THEME:-}" ]; then
  args+=("--dark-theme=${D2_DARK_THEME}")
fi
if [ "${D2_SKETCH:-0}" = "1" ]; then
  args+=("--sketch")
fi
if [ "${D2_WATCH:-0}" = "1" ]; then
  args+=("--watch")
fi

d2 "${args[@]}" "$input" "$output"
echo "rendered: $output"
