# Layout and medium guide

Three decisions that a correct-but-ugly diagram usually got wrong: which layout
engine drew it, whether anyone looked at the result, and what surface it was
designed for.

- [The render → inspect → revise loop](#the-render--inspect--revise-loop)
- [Choosing a layout engine](#choosing-a-layout-engine)
- [Output-medium profiles](#output-medium-profiles)
- [Multi-board storytelling](#multi-board-storytelling)

---

## The render → inspect → revise loop

A successful render proves the source compiles. It proves nothing about whether
the diagram works. `scripts/check_d2.sh` reports `ok` for a diagram with
unreadable 8px labels and forty crossing edges.

When rendering **and image inspection** are both available, run this loop:

1. Build the semantic model (IDs, labels, containers, edges) — no styling yet.
2. Style it deliberately: pick a style pack, layout engine, direction, type scale.
3. Render candidates. `scripts/review_d2.py diagram.d2` does the whole sweep:
   `d2 fmt --check`, `d2 validate`, a render per available engine, optional
   light/dark variants, and an HTML contact sheet.
4. Open or screenshot the result and **look at it**.
5. Inspect at the intended viewing size, not fit-to-window (see the scale trap
   below).
6. Name specific problems — "the failover edge is lost among six grey
   dependencies", not "it looks busy".
7. Revise and re-render.
8. Stop when it passes the
   [visual rubric](visual-design-guide.md#9-visual-rubric): 80+, no hard
   failures.

Two or three iterations is normal for a nontrivial architecture diagram. One is
optimistic.

### Inspecting the image

Reading the SVG's XML is not inspection. To actually see the diagram:

```bash
# Preferred: PNG straight from D2
d2 --scale 1 diagram.d2 /tmp/diagram.png

# Fallback when D2's PNG pipeline cannot fetch its browser (see troubleshooting):
d2 diagram.d2 /tmp/diagram.svg
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --window-size=1800,1200 --screenshot=/tmp/diagram.png /tmp/diagram.svg
```

`scripts/review_d2.py --png` does both, falling back automatically.

**The scale trap.** SVG output fits to its container by default, so a wide
diagram viewed in a browser window or a screenshot appears with uniformly small
text — including text that is 26px and perfectly fine at true size. Before
concluding "the type is too small", render with `--scale 1` (or `D2_SCALE=1`).
Conversely, a diagram that reads well fit-to-window may be 3000px wide and
unusable in a 700px docs column; check the aspect ratio and pixel width from the
SVG `viewBox`, not just the screenshot.

### When you cannot inspect

If the CLI is missing, PNG export is unavailable, or the environment cannot show
you an image, do the static review from
[rendering and validation](rendering-and-validation.md#validation-fallback-when-cli-is-unavailable)
and then **say what you did**: report the diagram as *statically reviewed but not
visually verified*. Do not present a compile success as a design verdict, and do
not report a rubric score for an image you never saw.

---

## Choosing a layout engine

For anything nontrivial, render **both ELK and Dagre** and compare, rather than
reasoning about which should win. They fail differently, and which failure
matters depends on the diagram.

| Engine | Availability | Strengths | Weaknesses |
|---|---|---|---|
| **dagre** | bundled, default | fast; good for small, shallow, directed graphs | curved multi-segment routes that wander; weaker handling of edges involving container children; crossings not minimized aggressively |
| **elk** | bundled | clean orthogonal routing; real crossing minimization; better native container routing; the safer default for dense hierarchies | slower; can produce tall results; less compact for tiny graphs |
| **tala** | separate install (proprietary) | designed for software architecture; considers symmetry and containers; supports extra positional control (`near` another object, `top`/`left` locks) | must be installed; more sensitive to small source changes; not available in most CI |

Practical defaults:

- Fewer than ~8 nodes, one level deep → `dagre` is usually fine and more compact.
- Containers, nested containers, or edges into container children → `elk`.
- Visible curved edges wandering across the diagram → switch to `elk`.
- ASCII output → `elk` (or `tala`), and keep the diagram simple.
- Architecture diagram you care about → render both, then choose. Render `tala`
  as a third candidate when it is installed.

Record the winner in the source so the diagram stays reproducible:

```d2
vars: {
  d2-config: {
    layout-engine: elk
  }
}
```

The bundled style packs already set an engine (`elk` for the documentation and
presentation packs, `dagre` for `sketch`); override it in the diagram when a
candidate render says otherwise.

`direction` (`up`/`down`/`left`/`right`) matters more than the engine for
readability. Request and dependency flows read left-to-right; pipelines, state
machines, and decision trees read top-down. Avoid manual positioning unless the
spatial arrangement is itself the information (a rack layout, a geographic map).

---

## Output-medium profiles

A diagram that is beautiful in a README is not a beautiful slide. Decide the
destination *before* styling, and record it in a comment.

### Web documentation (README, docs site, PR)

- **Format:** SVG
- **Style pack:** `minimal-light`, or `semantic-classes` + `theme-id` /
  `dark-theme-id` if the site has a dark mode
- Moderate detail is acceptable — the reader can zoom
- Put secondary information in `tooltip` and `link`; static exports turn tooltips
  into a numbered appendix automatically, and `--force-appendix` adds one to SVG
  too
- Watch the width: a 3000px-wide diagram in a 700px column is unreadable at
  as-published size even though it looks fine in a full-screen preview
- Never rely on text that only works at full-screen zoom

### Presentation (slides, screen share, demo)

- **Format:** SVG or PNG, composed for 16:9
- **Style pack:** `presentation`
- Larger labels, thicker primary edges, higher contrast, wider `pad`
- **Fewer components per board.** One clear focal path per slide
- Never shrink to fit — use layers/steps and advance through them (`.pptx` export
  puts each board on its own slide)

### Print / formal document

- **Format:** PDF
- **Style pack:** `minimal-light` (avoid very light strokes; they vanish in print)
- No hover: everything needed must be visible. `--force-appendix` materializes
  tooltips and links as an appendix
- **Include a legend** where the encoding is not self-evident — there is no
  tooltip to fall back on. See
  [legends](visual-design-guide.md#8-legends)
- Verify it survives grayscale

### Terminal / plain text

- **Format:** ASCII (`d2 in.d2 out.txt`, or `--stdout-format ascii`)
- `--ascii-mode=extended` (default) uses Unicode box characters;
  `--ascii-mode=standard` restricts to `+-|` for maximum portability
- **Layout:** `elk` or `tala`
- Keep it simple: a handful of nodes, one direction, short labels
- No color, shadow, icon, or dash may carry meaning — none of them survive
- ASCII output is still marked beta upstream; treat a poor result as a reason to
  simplify the diagram, not to fight the renderer

---

## Multi-board storytelling

Composition is not an advanced feature to reach for occasionally. It is the
**correct answer to overcrowding**, and the first thing to consider when a single
board passes 20 nodes or mixes abstraction levels.

> Do not solve excessive complexity by shrinking text or adding more colors.
> Split the visual story into boards.

For a large system, the conventional sequence of boards:

1. **System context** — the system as one box, plus its users and neighbours
2. **Container / service overview** — the major deployable pieces
3. **One runtime request flow** — the happy path, end to end
4. **Deployment topology** — regions, zones, clusters, networks
5. **One failure or failover scenario** — what changes when something breaks

Each board answers one question at one abstraction level. That is what makes each
of them legible; a merged version of all five is what makes a hairball.

D2 gives three composition mechanisms:

| Mechanism | Semantics | Use for |
|---|---|---|
| `layers` | a separate board, independent content | drill-down; the five boards above |
| `scenarios` | inherits the base board, then overrides | alternate states of the same system (normal vs. failover) |
| `steps` | inherits cumulatively from the previous step | walking through a sequence of changes |

Export options: multi-board SVG with `--animate-interval` for a self-advancing
diagram, `.gif` for embedding, `.pptx` for one slide per board, `.pdf` for a
document. Render one specific board with `--target='layers.deployment'`, or a
board plus its children with a trailing `*`.

See [the pattern cookbook](diagram-pattern-cookbook.md) for composition syntax
and `templates/composition-scenarios.d2` for a working starting point.

---

## Related

- [Visual design guide](visual-design-guide.md) — hierarchy, typography, color,
  edge hierarchy, density, icons, legends, and the rubric.
- [Rendering and validation](rendering-and-validation.md) — install, CLI flags,
  helper scripts, CI.
- [Troubleshooting](troubleshooting.md) — including the PNG/Playwright failure and
  the `**` glob conflict.
