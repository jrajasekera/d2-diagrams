#!/usr/bin/env python3
"""Produce layout candidates for a D2 diagram so a human or agent can look at them.

`check_d2.sh` answers "does this compile?". This answers "which of these looks
right?" - it checks formatting and syntax, renders one candidate per available
layout engine (optionally light and dark), reports geometry and smallest text
size per candidate, and writes an HTML contact sheet that shows them side by
side.

It does not judge the diagram. Open the contact sheet, or pass --png and read the
images, then score against the visual rubric in
references/visual-design-guide.md.

Usage:
  scripts/review_d2.py diagram.d2
  scripts/review_d2.py diagram.d2 --dark --png
  scripts/review_d2.py a.d2 b.d2 --engines elk,dagre --out-dir ./review
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Browsers tried, in order, when D2's own PNG pipeline is unavailable.
BROWSER_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "google-chrome",
    "chromium",
    "chromium-browser",
)

VIEWBOX_RE = re.compile(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"')
FONT_SIZE_RE = re.compile(r"font-size:\s*([\d.]+)")
COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


# D2's raster pipeline can hang trying to fetch its browser on a restricted
# network, which is exactly the case the browser fallback exists to survive - so
# every subprocess is bounded.
TIMEOUT_SECONDS = 90


def run(cmd: list[str], timeout: float = TIMEOUT_SECONDS) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            cmd, returncode=124, stdout="", stderr=f"timed out after {timeout:g}s"
        )


def available_engines() -> list[str]:
    """Layout engines this d2 install can actually use, in preference order."""
    result = run(["d2", "layout"])
    found = []
    for line in result.stdout.splitlines():
        match = re.match(r"^-?\s*(\w+)\s+\(", line.strip())
        if match:
            found.append(match.group(1))
    # Prefer elk first: it is the better default for anything with containers.
    order = {"elk": 0, "tala": 1, "dagre": 2}
    return sorted(found, key=lambda e: order.get(e, 99))


def find_browser() -> str | None:
    for candidate in BROWSER_CANDIDATES:
        if os.path.sep in candidate:
            if Path(candidate).exists():
                return candidate
        elif shutil.which(candidate):
            return shutil.which(candidate)
    return None


def svg_stats(path: Path) -> dict[str, object]:
    """Geometry and type-size facts that bear on the visual rubric."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    stats: dict[str, object] = {"bytes": path.stat().st_size}

    match = VIEWBOX_RE.search(text)
    if match:
        width = float(match.group(3))
        height = float(match.group(4))
        stats["width"] = round(width)
        stats["height"] = round(height)
        if height:
            stats["aspect"] = round(width / height, 2)

    sizes = sorted({float(s) for s in FONT_SIZE_RE.findall(text)})
    if sizes:
        stats["font_min"] = sizes[0]
        stats["font_max"] = sizes[-1]
        stats["font_sizes"] = len(sizes)

    return stats


def svg_colors(path: Path) -> set[str]:
    """Hex colors used in a render, for comparing a light and a dark variant."""
    try:
        return {c.lower() for c in COLOR_RE.findall(path.read_text(encoding="utf-8", errors="replace"))}
    except OSError:
        return set()


def render_svg(source: Path, out: Path, engine: str, theme: str | None) -> tuple[bool, str]:
    cmd = ["d2", f"--layout={engine}"]
    if theme is not None:
        cmd.append(f"--theme={theme}")
    cmd += [str(source), str(out)]
    result = run(cmd)
    return result.returncode == 0, (result.stderr or result.stdout).strip()


def render_png(svg: Path, png: Path, source: Path, engine: str, theme: str | None,
               scale: float, browser: str | None) -> tuple[bool, str]:
    """PNG via D2, falling back to a headless browser screenshot of the SVG.

    D2's PNG/PDF/PPTX pipeline downloads a Playwright browser on first use, which
    fails in sandboxes and offline CI. The SVG already exists at that point, so a
    local browser can screenshot it instead.
    """
    cmd = ["d2", f"--layout={engine}", f"--scale={scale}"]
    if theme is not None:
        cmd.append(f"--theme={theme}")
    cmd += [str(source), str(png)]
    result = run(cmd)
    if result.returncode == 0 and png.exists():
        return True, "d2"

    if browser is None:
        return False, "d2 png export failed and no headless browser found"

    # Screenshot a scaled SVG, not the default one. `--scale` writes absolute
    # dimensions instead of fit-to-screen, so sizing the window to the result
    # captures the diagram at true size - otherwise this fallback would hand back
    # an image at exactly the fit-to-window scale the guide calls the scale trap.
    scaled = svg.with_name(f"{svg.stem}.scaled.svg")
    cmd = ["d2", f"--layout={engine}", f"--scale={scale}"]
    if theme is not None:
        cmd.append(f"--theme={theme}")
    cmd += [str(source), str(scaled)]
    shot_source = scaled if run(cmd).returncode == 0 and scaled.exists() else svg

    stats = svg_stats(shot_source)
    width = int(float(stats.get("width", 1600)) + 40)
    height = int(float(stats.get("height", 900)) + 40)
    if width > 8000 or height > 8000:
        return False, f"diagram is {width}x{height}px; too large to screenshot at scale {scale:g}"

    shot = run([
        browser,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={png}",
        str(shot_source),
    ])
    if shot_source is scaled:
        scaled.unlink(missing_ok=True)
    if png.exists():
        return True, f"browser at scale {scale:g}"
    return False, (shot.stderr or "browser screenshot failed").strip()


def contact_sheet(out_dir: Path, groups: list[dict[str, object]]) -> Path:
    """One HTML page showing every candidate side by side."""
    parts = [
        "<title>D2 layout candidates</title>",
        "<style>",
        "  :root { color-scheme: light dark; }",
        "  body { font: 14px/1.5 ui-sans-serif, system-ui, sans-serif; margin: 2rem; }",
        "  h1 { font-size: 1.4rem; }",
        "  h2 { font-size: 1.1rem; margin-top: 2.5rem; border-bottom: 1px solid #8884; padding-bottom: .4rem; }",
        "  .grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); }",
        "  figure { margin: 0; border: 1px solid #8884; border-radius: 8px; overflow: hidden; }",
        "  figcaption { padding: .6rem .8rem; background: #8881; font-weight: 600; }",
        "  figcaption span { font-weight: 400; opacity: .75; }",
        "  .frame { background: #fff; overflow: auto; max-height: 70vh; }",
        "  .frame.dark { background: #14141c; }",
        "  .frame img { display: block; width: 100%; }",
        "  .fail { padding: .8rem; color: #b91c1c; white-space: pre-wrap; font-family: ui-monospace, monospace; }",
        "  .hint { background: #8881; padding: .8rem 1rem; border-radius: 8px; }",
        "</style>",
        "<h1>D2 layout candidates</h1>",
        "<p class=hint>Compare these at the size the diagram will actually be used at, "
        "then score against the visual rubric "
        "(<code>references/visual-design-guide.md</code>). Target 80+ with no hard failures. "
        "Wide diagrams are scaled to fit here &mdash; check <em>width</em> below before "
        "concluding the type is too small.</p>",
    ]

    for group in groups:
        parts.append(f"<h2>{html.escape(str(group['source']))}</h2>")
        parts.append("<div class=grid>")
        for cand in group["candidates"]:  # type: ignore[index]
            label = html.escape(cand["label"])
            if not cand["ok"]:
                parts.append(
                    f"<figure><figcaption>{label}</figcaption>"
                    f"<div class=fail>{html.escape(cand['error'])}</div></figure>"
                )
                continue
            stats = cand["stats"]
            meta = []
            if "width" in stats:
                meta.append(f"{stats['width']}&times;{stats['height']}px")
            if "aspect" in stats:
                meta.append(f"aspect {stats['aspect']}")
            if "font_min" in stats:
                meta.append(f"text {stats['font_min']:g}&ndash;{stats['font_max']:g}px")
            frame_class = "frame dark" if cand["dark"] else "frame"
            parts.append(
                f"<figure><figcaption>{label} <span>{' &middot; '.join(meta)}</span></figcaption>"
                f"<div class='{frame_class}'><img src='{html.escape(cand['file'])}' alt='{label}'></div>"
                f"</figure>"
            )
        parts.append("</div>")

    sheet = out_dir / "contact-sheet.html"
    sheet.write_text("\n".join(parts), encoding="utf-8")
    return sheet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("sources", nargs="+", help=".d2 files to review")
    parser.add_argument(
        "--engines",
        help="comma-separated layout engines (default: every engine this d2 install has)",
    )
    parser.add_argument("--theme", help="light theme id (default: whatever the source sets)")
    parser.add_argument("--dark-theme", default="200", help="theme id used for --dark (default 200)")
    parser.add_argument("--dark", action="store_true", help="also render a dark variant per engine")
    parser.add_argument("--png", action="store_true", help="also write PNGs, for agents that read images")
    parser.add_argument("--scale", type=float, default=1.0, help="PNG scale (default 1, i.e. true size)")
    parser.add_argument("--out-dir", help="keep output here instead of a temp directory")
    parser.add_argument("--open", action="store_true", help="open the contact sheet when done")
    args = parser.parse_args(argv)

    if not shutil.which("d2"):
        die(
            "d2 CLI not found on PATH. Install from https://d2lang.com/tour/install/ "
            "or review the source statically.",
            127,
        )

    sources = [Path(s) for s in args.sources]
    for source in sources:
        if not source.is_file():
            die(f"input file not found: {source}")

    engines = (
        [e.strip() for e in args.engines.split(",") if e.strip()]
        if args.engines
        else available_engines()
    )
    if not engines:
        die("no layout engines reported by `d2 layout`")

    if args.out_dir:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = Path(tempfile.mkdtemp(prefix="d2-review-"))

    browser = find_browser() if args.png else None
    if args.png and browser is None:
        print("note: no headless browser found; PNG output depends on d2's own export pipeline")

    print(f"engines: {', '.join(engines)}")
    print(f"output:  {out_dir}")

    status = 0
    groups: list[dict[str, object]] = []

    for source in sources:
        print(f"\n=== {source}")

        fmt = run(["d2", "fmt", "--check", str(source)])
        if fmt.returncode == 0:
            print("  fmt      ok")
        else:
            # A warning, not a failure. This tool reviews how a diagram looks;
            # `check_d2.sh` and CI are where formatting is enforced.
            print(f"  fmt      unformatted (run: d2 fmt {source})")

        valid = run(["d2", "validate", str(source)])
        if valid.returncode == 0:
            print("  validate ok")
        else:
            print("  validate FAILED")
            print("    " + (valid.stderr or valid.stdout).strip().replace("\n", "\n    "))
            groups.append({"source": str(source), "candidates": []})
            status = 1
            continue

        variants = [("light", args.theme, False)]
        if args.dark:
            variants.append(("dark", args.dark_theme, True))

        candidates = []
        for engine in engines:
            for variant, theme, is_dark in variants:
                stem = f"{source.stem}.{engine}.{variant}"
                svg = out_dir / f"{stem}.svg"
                label = f"{engine} / {variant}"
                ok, message = render_svg(source, svg, engine, theme)
                if not ok:
                    print(f"  {label:<16} FAILED")
                    print("    " + message.replace("\n", "\n    "))
                    candidates.append(
                        {"label": label, "ok": False, "error": message, "dark": is_dark}
                    )
                    status = 1
                    continue

                stats = svg_stats(svg)
                summary = []
                if "width" in stats:
                    summary.append(f"{stats['width']}x{stats['height']}px")
                if "aspect" in stats:
                    summary.append(f"aspect {stats['aspect']}")
                if "font_min" in stats:
                    summary.append(
                        f"text {stats['font_min']:g}-{stats['font_max']:g}px "
                        f"({stats['font_sizes']} sizes)"
                    )
                print(f"  {label:<16} {svg.name}  {'  '.join(summary)}")

                shown = svg.name
                if args.png:
                    png = out_dir / f"{stem}.png"
                    png_ok, how = render_png(svg, png, source, engine, theme, args.scale, browser)
                    if png_ok:
                        print(f"  {'':<16} {png.name}  (via {how})")
                        shown = png.name
                    else:
                        print(f"  {'':<16} png unavailable: {how}")

                candidates.append(
                    {
                        "label": label,
                        "ok": True,
                        "file": shown,
                        "stats": stats,
                        "dark": is_dark,
                    }
                )

            # When the dark render reuses most of the light render's hex colors,
            # explicit fill/stroke values are overriding the theme and the
            # diagram is not adaptive. That is deliberate for a hand-coloured
            # pack like minimal-light and a bug for anything meant to follow the
            # viewer, so this reports rather than judges.
            if args.dark:
                light_svg = out_dir / f"{source.stem}.{engine}.light.svg"
                dark_svg = out_dir / f"{source.stem}.{engine}.dark.svg"
                if light_svg.exists() and dark_svg.exists():
                    light_colors = svg_colors(light_svg)
                    dark_colors = svg_colors(dark_svg)
                    union = light_colors | dark_colors
                    if union and len(light_colors & dark_colors) / len(union) >= 0.35:
                        print(
                            f"  {'':<16} note: the dark render reuses most of the light "
                            "palette, so explicit fills are overriding the theme. Intended "
                            "for a hand-coloured pack; a bug if this diagram should adapt."
                        )

        groups.append({"source": str(source), "candidates": candidates})

    sheet = contact_sheet(out_dir, groups)
    print(f"\ncontact sheet: {sheet}")
    print("Open it, or read the PNGs, then score against the visual rubric in")
    print("references/visual-design-guide.md. Do not report a score for an image you did not see.")

    if args.open:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        if shutil.which(opener):
            run([opener, str(sheet)])

    return status


if __name__ == "__main__":
    raise SystemExit(main())
