#!/usr/bin/env python3
"""Copy starter D2 templates from this skill into a target file."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"


def template_map() -> dict[str, Path]:
    return {p.stem: p for p in sorted(TEMPLATES.glob("*.d2"))}


def cmd_list(_: argparse.Namespace) -> int:
    for name, path in template_map().items():
        first = ""
        try:
            with path.open("r", encoding="utf-8") as fh:
                first = fh.readline().strip().lstrip("# ")
        except OSError:
            pass
        suffix = f" - {first}" if first else ""
        print(f"{name}{suffix}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    templates = template_map()
    src = templates.get(args.template)
    if src is None:
        print(f"error: unknown template '{args.template}'", file=sys.stderr)
        print("available templates:", file=sys.stderr)
        for name in templates:
            print(f"  {name}", file=sys.stderr)
        return 2

    dest = Path(args.output)
    if dest.exists() and not args.force:
        print(f"error: output exists: {dest} (use --force to overwrite)", file=sys.stderr)
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    print(f"created: {dest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list available templates")
    p_list.set_defaults(func=cmd_list)

    p_create = sub.add_parser("create", help="copy a template to an output path")
    p_create.add_argument("template", help="template name from list")
    p_create.add_argument("output", help="destination .d2 path")
    p_create.add_argument("--force", action="store_true", help="overwrite output if it exists")
    p_create.set_defaults(func=cmd_create)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
