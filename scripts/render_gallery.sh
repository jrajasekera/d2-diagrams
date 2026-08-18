#!/usr/bin/env bash
# Regenerate the committed gallery previews, or check them for drift.
#
# gallery/**/preview.svg is the one exception to "renders are disposable": those
# files are teaching material, so they are committed. That makes them a cheap
# visual regression test - if a D2 upgrade or a style-pack edit changes a
# reference diagram, `--check` says so.
#
#   scripts/render_gallery.sh            # rewrite every preview.svg
#   scripts/render_gallery.sh --check    # fail if any preview is out of date
#
# A --check failure is information, not necessarily a bug. Renderer versions
# differ. Look at the new image before deciding: if it is better, commit it; if
# it is worse, that is the regression you wanted to catch. Record the D2 version
# the previews were generated with in the commit message.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v d2 >/dev/null 2>&1; then
  echo "error: d2 CLI not found on PATH. Install from https://d2lang.com/tour/install/." >&2
  exit 127
fi

check=0
if [ "${1:-}" = "--check" ]; then
  check=1
elif [ "$#" -gt 0 ]; then
  echo "usage: $0 [--check]" >&2
  exit 2
fi

echo "d2 $(d2 --version)"

status=0
found=0
for source in "$ROOT"/gallery/*/diagram.d2; do
  [ -e "$source" ] || continue
  found=1
  dir="$(dirname "$source")"
  name="$(basename "$dir")"
  preview="$dir/preview.svg"

  # --omit-version keeps a d2 upgrade from showing up as a diff in every file.
  tmp="$(mktemp -d)"
  if ! log="$(d2 --omit-version "$source" "$tmp/preview.svg" 2>&1)"; then
    echo "failed: $name" >&2
    echo "$log" >&2
    rm -rf "$tmp"
    status=1
    continue
  fi

  # A diagram with layers/scenarios/steps renders one file per board into a
  # directory. Re-render those as a single animated SVG so the preview stays one
  # committed file.
  if [ ! -f "$tmp/preview.svg" ]; then
    rm -rf "$tmp"
    tmp="$(mktemp -d)"
    if ! log="$(d2 --omit-version --animate-interval=2000 "$source" "$tmp/preview.svg" 2>&1)"; then
      echo "failed: $name (multi-board)" >&2
      echo "$log" >&2
      rm -rf "$tmp"
      status=1
      continue
    fi
  fi

  if [ "$check" -eq 1 ]; then
    if [ ! -f "$preview" ]; then
      echo "missing: $name/preview.svg (run: scripts/render_gallery.sh)" >&2
      status=1
    elif ! cmp -s "$tmp/preview.svg" "$preview"; then
      echo "drift:   $name/preview.svg differs from a fresh render" >&2
      status=1
    else
      echo "ok:      $name"
    fi
  else
    mv "$tmp/preview.svg" "$preview"
    echo "wrote:   ${preview#"$ROOT"/}"
  fi
  rm -rf "$tmp"
done

if [ "$found" -eq 0 ]; then
  echo "error: no gallery/*/diagram.d2 files found" >&2
  exit 1
fi

exit "$status"
