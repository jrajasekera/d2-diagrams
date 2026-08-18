#!/usr/bin/env python3
"""Start a diagram from a bundled template, wired to a bundled style pack.

Templates carry structure (what shapes, what containers, what edges). Style packs
carry the visual system (palette, type scale, edge hierarchy). This composes the
two and copies the style pack next to the output, so the new diagram does not
depend on where this skill happens to be installed.

  scaffold_d2.py list                                   # templates
  scaffold_d2.py styles                                 # style packs
  scaffold_d2.py create system-architecture arch.d2
  scaffold_d2.py create system-architecture deck.d2 --style presentation
  scaffold_d2.py create event-driven post.d2 --medium editorial
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
STYLES = ROOT / "styles"

IMPORT_RE = re.compile(r"^\.\.\.@(?P<path>\S+)\s*$", re.MULTILINE)

# Output destination -> (default style pack, note written into the file header).
MEDIUMS = {
    "docs": (
        "minimal-light",
        "READMEs, design docs, wikis. SVG, moderate detail, tooltips for the rest.",
    ),
    "adaptive": (
        "semantic-classes",
        "Docs sites with a dark mode. No explicit fills - set theme-id and "
        "dark-theme-id and let the viewer's mode decide.",
    ),
    "dark": (
        "minimal-dark",
        "Destinations known to be dark. Not adaptive: light-mode viewers still "
        "see dark shapes.",
    ),
    "slides": (
        "presentation",
        "16:9 slides. Larger type, heavier strokes, fewer nodes per board - "
        "split into layers rather than shrinking.",
    ),
    "print": (
        "minimal-light",
        "PDF or paper. No hover, so add a legend; avoid hairline strokes; check "
        "it survives grayscale.",
    ),
    "editorial": (
        "editorial",
        "Blog posts and long-form writing. A little personality, generous type.",
    ),
    "sketch": (
        "sketch",
        "Proposals and drafts. The hand-drawn look tells the reader to argue "
        "with it.",
    ),
    "terminal": (
        "semantic-classes",
        "ASCII output (d2 in.d2 out.txt). Keep it small; color, dash, shadow, "
        "and icons all disappear.",
    ),
}


def template_map() -> dict[str, Path]:
    return {p.stem: p for p in sorted(TEMPLATES.glob("*.d2"))}


def style_map() -> dict[str, Path]:
    return {p.stem: p for p in sorted(STYLES.glob("*.d2"))}


def first_comment(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line.startswith("#"):
                    return line.lstrip("# ").strip()
                if line:
                    return ""
    except OSError:
        pass
    return ""


def cmd_list(_: argparse.Namespace) -> int:
    for name, path in template_map().items():
        description = first_comment(path)
        print(f"{name}{f' - {description}' if description else ''}")
    return 0


def best_for(path: Path) -> str:
    """The `# Best for:` line of a style pack, which is its real description."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("# Best for:"):
                return stripped.removeprefix("# Best for:").strip()
            if stripped and not stripped.startswith("#"):
                break
    except OSError:
        pass
    return first_comment(path).removeprefix("Style pack: ")


def cmd_styles(_: argparse.Namespace) -> int:
    for name, path in style_map().items():
        description = best_for(path)
        print(f"{name:<17}{description}")
    print("\nmediums:")
    for name, (style, note) in MEDIUMS.items():
        print(f"  {name:<9} -> {style:<17} {note}")
    return 0


def style_closure(name: str, styles: dict[str, Path]) -> list[Path]:
    """A style pack plus everything it imports, in copy order."""
    seen: list[Path] = []
    pending = [name]
    while pending:
        current = pending.pop()
        path = styles.get(current)
        if path is None or path in seen:
            continue
        seen.append(path)
        for match in IMPORT_RE.finditer(path.read_text(encoding="utf-8")):
            pending.append(Path(match.group("path")).stem)
    return seen


def cmd_create(args: argparse.Namespace) -> int:
    templates = template_map()
    source = templates.get(args.template)
    if source is None:
        print(f"error: unknown template '{args.template}'", file=sys.stderr)
        print("available templates:", file=sys.stderr)
        for name in templates:
            print(f"  {name}", file=sys.stderr)
        return 2

    styles = style_map()
    medium_note = ""
    style_name = args.style
    if args.medium:
        if args.medium not in MEDIUMS:
            print(f"error: unknown medium '{args.medium}'", file=sys.stderr)
            print(f"available mediums: {', '.join(MEDIUMS)}", file=sys.stderr)
            return 2
        default_style, medium_note = MEDIUMS[args.medium]
        style_name = style_name or default_style

    if style_name and style_name not in styles:
        print(f"error: unknown style '{style_name}'", file=sys.stderr)
        print(f"available styles: {', '.join(styles)}", file=sys.stderr)
        return 2

    destination = Path(args.output)
    if destination.exists() and not args.force:
        print(f"error: output exists: {destination} (use --force to overwrite)", file=sys.stderr)
        return 1
    destination.parent.mkdir(parents=True, exist_ok=True)

    text = source.read_text(encoding="utf-8")

    # A template's imports are either a style pack (rewritable, and the point of
    # --style) or a sibling template it depends on (must be copied verbatim, or
    # the output will not compile).
    style_import = None
    sibling_imports: list[Path] = []
    for match in IMPORT_RE.finditer(text):
        stem = Path(match.group("path")).stem
        if stem in styles:
            if style_import is None:
                style_import = match.group(0)
        else:
            sibling = TEMPLATES / f"{stem}.d2"
            if not sibling.is_file():
                print(
                    f"error: {source.name} imports '{stem}', which is neither a style pack "
                    f"nor a template in {TEMPLATES}. Cannot produce a diagram that compiles.",
                    file=sys.stderr,
                )
                return 1
            sibling_imports.append(sibling)

    # Restyling a template whose classes come from a sibling import would leave
    # every `class:` reference dangling, and D2 ignores unknown classes silently
    # - it compiles and quietly loses all styling. Refuse instead.
    if (args.style or args.medium) and sibling_imports:
        print(
            f"error: template '{args.template}' carries its own style file "
            f"({', '.join(p.stem for p in sibling_imports)}), so --style/--medium cannot "
            "be applied to it without dropping the styling it defines.",
            file=sys.stderr,
        )
        print(
            "       Use a template that imports a style pack, e.g. system-architecture.",
            file=sys.stderr,
        )
        return 2

    # Without an explicit --style/--medium, keep whatever pack the template uses.
    if style_name is None and style_import is not None:
        style_name = Path(style_import.removeprefix("...@").strip()).stem

    copied: list[Path] = []
    for sibling in sibling_imports:
        target = destination.parent / sibling.name
        shutil.copyfile(sibling, target)
        copied.append(target)

    if style_name:
        style_dir = destination.parent / "styles"
        style_dir.mkdir(parents=True, exist_ok=True)
        for path in style_closure(style_name, styles):
            target = style_dir / path.name
            shutil.copyfile(path, target)
            copied.append(target)

        import_line = f"...@styles/{style_name}"
        if style_import is not None:
            text = text.replace(style_import, import_line, 1)
        else:
            text = f"{import_line}\n\n{text}"

    if args.medium:
        header = f"# Medium: {args.medium}. {medium_note}\n"
        text = header + text

    destination.write_text(text, encoding="utf-8")
    print(f"created: {destination}")
    for path in copied:
        print(f"  needs:  {path}")
    print(f"\nNext: render it, look at the image, and revise. Do not stop at 'it compiled'.")
    print(f"  scripts/review_d2.py {destination}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list available templates")
    p_list.set_defaults(func=cmd_list)

    p_styles = sub.add_parser("styles", help="list style packs and medium profiles")
    p_styles.set_defaults(func=cmd_styles)

    p_create = sub.add_parser("create", help="copy a template, wired to a style pack")
    p_create.add_argument("template", help="template name from `list`")
    p_create.add_argument("output", help="destination .d2 path")
    p_create.add_argument("--style", help="style pack from `styles` (default: the template's own)")
    p_create.add_argument(
        "--medium",
        help=f"output destination, which picks a default style: {', '.join(MEDIUMS)}",
    )
    p_create.add_argument("--force", action="store_true", help="overwrite output if it exists")
    p_create.set_defaults(func=cmd_create)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
