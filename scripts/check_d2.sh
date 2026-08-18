#!/usr/bin/env bash
# Check D2 source files: syntax (d2 validate), then compile+render (the semantic
# check), and optionally formatting.
#
# A pass here means "D2 can draw this". It does NOT mean the diagram is any good.
# For visual review, use scripts/review_d2.py and look at the image.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: scripts/check_d2.sh <file.d2> [more.d2 ...]

Per file: d2 validate (syntax), then render to a throwaway SVG (compile).
Prints ok/failed per file; exits non-zero if any file fails.

Environment:
  D2_LAYOUT=elk|dagre|tala   layout engine used for the render check
  D2_THEME=<id>              theme used for the render check
  D2_FMT=1                   also require `d2 fmt --check` to pass
EOF
}

if ! command -v d2 >/dev/null 2>&1; then
  echo "error: d2 CLI not found on PATH. Install from https://d2lang.com/tour/install/ or use this skill source-only." >&2
  exit 127
fi

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

status=0
for file in "$@"; do
  if [ ! -f "$file" ]; then
    echo "missing: $file" >&2
    status=1
    continue
  fi

  # 1. Syntax. Cheap, and gives the clearest parse errors.
  if ! log="$(d2 validate "$file" 2>&1)"; then
    echo "failed (syntax): $file" >&2
    echo "$log" >&2
    status=1
    continue
  fi

  # 2. Formatting, opt-in. `d2 validate` accepts unformatted-but-valid source.
  if [ "${D2_FMT:-0}" = "1" ] && ! d2 fmt --check "$file" >/dev/null 2>&1; then
    echo "failed (unformatted, run: d2 fmt $file): $file" >&2
    status=1
    continue
  fi

  # 3. Compile + render. This is the real check: `d2 validate` only parses, so
  #    unresolved keys, bad indexed edges, and bad imports still get through it.
  tmpdir="$(mktemp -d)"
  out="$tmpdir/$(basename "${file%.d2}").svg"
  args=()
  if [ -n "${D2_LAYOUT:-}" ]; then
    args+=("--layout=${D2_LAYOUT}")
  fi
  if [ -n "${D2_THEME:-}" ]; then
    args+=("--theme=${D2_THEME}")
  fi

  if log="$(d2 ${args[@]+"${args[@]}"} "$file" "$out" 2>&1)"; then
    echo "ok: $file"
  else
    echo "failed (render): $file" >&2
    echo "$log" >&2
    status=1
  fi
  rm -rf "$tmpdir"
done

exit "$status"
