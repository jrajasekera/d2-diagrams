#!/usr/bin/env python3
"""Compile every fenced ```d2 example in the package's Markdown.

Documentation drifts away from the language faster than templates do, because
nothing ever runs it. This extracts each fenced `d2` block and renders it, so a
snippet that stopped being valid D2 fails here instead of in a user's editor.

Style-pack imports work: blocks are compiled beside a link to the real `styles/`,
so both `...@styles/minimal-light` and `...@../styles/minimal-light` resolve.

Skipping a block: put `<!-- validate:skip -->` on the line before the fence, or
use the ```d2 skip info string. Use it for deliberate counter-examples ("this is
wrong, do not do this") and for fragments that cannot stand alone, such as ones
importing a file that only exists in another directory.

Usage:
  scripts/validate_docs.py                     # all Markdown in the package
  scripts/validate_docs.py SKILL.md            # specific files
  scripts/validate_docs.py --list              # show blocks without rendering
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOBS = ("*.md", "references/*.md", "gallery/*/*.md")

SKIP_MARKER = "<!-- validate:skip -->"


class Block:
    def __init__(self, path: Path, line: int, code: str, skip: bool) -> None:
        self.path = path
        self.line = line
        self.code = code
        self.skip = skip

    @property
    def label(self) -> str:
        return f"{self.path.relative_to(ROOT)}:{self.line}"


def extract(path: Path) -> list[Block]:
    """Find fenced d2 blocks. Tracks fence characters so nested fences behave."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    blocks: list[Block] = []

    open_fence: str | None = None
    info = ""
    start = 0
    buffer: list[str] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if open_fence is None:
            match = re.match(r"^(```+|~~~+)[ \t]*(.*)$", stripped)
            if match:
                open_fence = match.group(1)[0] * 3
                info = match.group(2).strip()
                start = index + 1
                buffer = []
            continue

        if stripped.startswith(open_fence) and not stripped[len(open_fence):].strip():
            language, _, modifier = info.partition(" ")
            if language == "d2":
                previous = lines[start - 2].strip() if start >= 2 else ""
                skip = modifier.strip() == "skip" or previous == SKIP_MARKER
                blocks.append(Block(path, start, "\n".join(buffer), skip))
            open_fence = None
            continue

        buffer.append(line)

    return blocks


def collect(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p).resolve() for p in paths]
    found: list[Path] = []
    for pattern in DEFAULT_GLOBS:
        found.extend(sorted(ROOT.glob(pattern)))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", help="Markdown files (default: the whole package)")
    parser.add_argument("--list", action="store_true", help="list blocks instead of rendering them")
    parser.add_argument("--layout", default="dagre", help="layout engine (default dagre, it is fastest)")
    args = parser.parse_args(argv)

    files = collect(args.paths)
    blocks = [b for f in files if f.is_file() for b in extract(f)]

    if args.list:
        for block in blocks:
            state = "skip" if block.skip else "check"
            first = block.code.strip().split("\n", 1)[0][:60]
            print(f"{state:<6} {block.label:<48} {first}")
        print(f"\n{len(blocks)} d2 blocks in {len(files)} files")
        return 0

    if not shutil.which("d2"):
        print(
            "error: d2 CLI not found on PATH. Install from https://d2lang.com/tour/install/.",
            file=sys.stderr,
        )
        return 127

    checked = skipped = failed = 0
    with tempfile.TemporaryDirectory(prefix="d2-docs-") as tmp:
        # Blocks live one level down, with a link to the real styles/ both
        # beside and above them, so a doc example resolves whether it imports
        # `styles/minimal-light` (the scaffolded layout) or `../styles/...`
        # (the in-package layout used by templates/ and gallery/*/).
        tmpdir = Path(tmp) / "docs"
        tmpdir.mkdir()
        for parent in (Path(tmp), tmpdir):
            (parent / "styles").symlink_to(ROOT / "styles", target_is_directory=True)

        for index, block in enumerate(blocks):
            if block.skip:
                skipped += 1
                continue
            if not block.code.strip():
                continue

            source = tmpdir / f"block{index}.d2"
            source.write_text(block.code + "\n", encoding="utf-8")
            result = subprocess.run(
                ["d2", f"--layout={args.layout}", str(source), str(tmpdir / f"block{index}.svg")],
                capture_output=True,
                text=True,
            )
            checked += 1
            if result.returncode != 0:
                failed += 1
                message = (result.stderr or result.stdout).strip()
                # The temp path in the error is noise; the doc location is not.
                message = message.replace(str(source), block.label)
                print(f"FAILED {block.label}", file=sys.stderr)
                print("  " + message.replace("\n", "\n  "), file=sys.stderr)

    print(f"{checked} checked, {skipped} skipped, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
