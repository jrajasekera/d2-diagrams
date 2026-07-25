#!/usr/bin/env bash
set -euo pipefail

if ! command -v d2 >/dev/null 2>&1; then
  echo "error: d2 CLI not found on PATH. Install from https://d2lang.com/tour/install/ or use this skill source-only." >&2
  exit 127
fi

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <file.d2> [more.d2 ...]" >&2
  exit 2
fi

status=0
for file in "$@"; do
  if [ ! -f "$file" ]; then
    echo "missing: $file" >&2
    status=1
    continue
  fi

  tmpdir="$(mktemp -d)"
  out="$tmpdir/$(basename "${file%.d2}").svg"
  args=()
  if [ -n "${D2_LAYOUT:-}" ]; then
    args+=("--layout=${D2_LAYOUT}")
  fi
  if [ -n "${D2_THEME:-}" ]; then
    args+=("--theme=${D2_THEME}")
  fi

  if d2 ${args[@]+"${args[@]}"} "$file" "$out" >/dev/null; then
    echo "ok: $file"
  else
    echo "failed: $file" >&2
    status=1
  fi
  rm -rf "$tmpdir"
done

exit "$status"
