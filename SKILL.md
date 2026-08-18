---
name: d2-diagrams
description: Design, create, edit, review, validate, render, and troubleshoot D2 declarative diagrams (.d2) for architecture, flowcharts, sequence diagrams, ERDs, UML classes, network/cloud topology, CI/CD, event flows, grids, compositions, themes, icons, legends, and documentation exports. Produces visually reviewed, presentation-ready diagrams with a semantic style system, not just source that compiles. Use when the user asks for D2, diagram-as-code, text-to-diagram, SVG/PNG/PDF/PPTX/GIF/ASCII rendering, or converting Mermaid/PlantUML/Graphviz/whiteboard descriptions into D2.
license: MIT
compatibility: Agent Skills standard. Compatible with Claude Code, Codex, Hermes Agent, and Pi. Optional d2 CLI improves validation/rendering; no network required unless fetching remote icons/images.
metadata:
  version: "2.0.0"
  language: d2
  formats: "svg,png,pdf,pptx,gif,ascii"
---

# D2 Diagrams

Use this skill to design D2 diagrams that people can actually read, revise
existing `.d2` files, convert other diagram descriptions into D2, and render or
validate them when the D2 CLI is available.

D2 is declarative: describe the system, relationships, containers, styles, and
layout hints, and the renderer computes the drawing. But the renderer has no
opinion about whether a human can read the result. **A successful render is not a
quality gate.** Design the picture, then look at it.

## Core workflow

1. **Establish the visual brief.** Audience, destination, target size or aspect
   ratio, the one-sentence takeaway, the primary flow, how much detail is wanted,
   whether light/dark both matter, and whether icons are allowed. Pick sensible
   defaults rather than stalling: SVG for documentation, `direction: right` for
   request flows, `direction: down` for pipelines, `styles/minimal-light.d2`,
   no icons.
2. **Choose one abstraction level.** Context, container, component, deployment,
   data, sequence, process, or schema — one of them, not a mix. If the request
   spans levels, that is several boards, not one crowded diagram.
3. **Build the semantic model before styling.** Stable snake_case IDs, concise
   labels, meaningful containers, and only the relationships the thesis needs.
4. **Select a visual system.** Import a style pack, then choose layout engine,
   direction, type scale, and edge hierarchy for this diagram.
5. **Render candidates.** For anything nontrivial, render both `elk` and `dagre`
   and compare; add `tala` when installed. `scripts/review_d2.py diagram.d2`
   does the whole sweep and writes a contact sheet.
6. **Inspect the rendered artifact.** Open the image, or `--png` and read it.
   Check hierarchy, legibility at the destination size, whitespace, routing,
   crossings, balance, and whether the thesis is what you see in three seconds.
7. **Revise deliberately.** Shorten labels, cut low-value edges, resize hub
   nodes, restructure containers, split overcrowded views, change engine or
   style. Re-render after any material change. Two or three passes is normal.
8. **Deliver the whole result.** The canonical `.d2` source, the chosen render,
   the layout engine and theme used, and any notes about other boards. If you
   could not see the image, say the diagram is **statically reviewed but not
   visually verified**.

Steps 5–7 are the loop that matters. Skipping them and shipping the first thing
that compiled is the single biggest quality gap in generated diagrams.

## Visual rules

The full system lives in
[the visual design guide](references/visual-design-guide.md). These are the rules
that apply every time:

- **State the thesis.** One sentence, in a comment at the top of the file. If you
  cannot name the focal node or path, the model is not finished and styling is
  premature.
- **Containers are quieter than their contents.** A boundary is a frame, not a
  participant.
- **Emphasise with weight and contrast, not a new color.** Heavier stroke, bolder
  label, larger node — same hue family.
- **Neutral + one accent + one data family + status.** Red, amber, and green are
  reserved for failure, warning, and success. Spending them decoratively means
  there is no color left to signal a real problem.
- **Never encode meaning in color alone.** Pair every color distinction with
  shape, dash, stroke weight, or the label — the status classes ship solid /
  dashed / double borders for exactly this reason.
- **Give edges a hierarchy.** Primary flow heavy and labeled; dependencies thin;
  async dashed; failure dashed and labeled. Every edge must earn its place.
- **Three type tiers among the shapes**, one size for all edge labels, one or
  two lines per label. Set sizes on classes, not on individual nodes.
- **Past ~20 nodes, split the diagram.** Do not solve crowding by shrinking text
  or adding colors. Split the visual story into boards.
- **Add a legend** when the encoding is not self-evident, and always for print.
- **Icons: one family, not on every node, and the diagram must survive their
  removal.**

## Style packs

`styles/` holds the visual system, so diagrams do not each invent a palette.

```d2
...@../styles/minimal-light

api: API Service {class: primary_service}
db: PostgreSQL {class: datastore}
api -> db: SQL {class: primary_edge}
```

| Pack | Use for |
|---|---|
| `semantic-classes` | structure only, no colors — the light/dark **adaptive** choice, and the base of every other pack |
| `minimal-light` | READMEs, design docs, wikis, PRs |
| `minimal-dark` | destinations known to be dark |
| `presentation` | slides: bigger type, heavier strokes, wider padding |
| `editorial` | blog posts and long-form writing |
| `sketch` | proposals and drafts, hand-drawn |

Classes available in all of them: `actor`, `external_system`, `boundary`,
`primary_service`, `secondary_service`, `datastore`, `queue`, `decision`,
`annotation`, `success`, `warning`, `failure`, `primary_edge`, `secondary_edge`,
`async_edge`, `fallback_edge`.

Explicit `fill`/`stroke` values override D2's dark theme. For one diagram that
follows the viewer's mode, import `semantic-classes` and set `theme-id` plus
`dark-theme-id` — not a hand-colored pack.

## Essential D2 syntax

```d2
# Direction is a layout hint: up, down, left, right
direction: right

# Stable IDs with human labels
api: API Gateway
web: Web App
db: PostgreSQL
cache: Redis Cache

# Shape attributes
db.shape: cylinder
cache.shape: stored_data

# Four connection operators: --, ->, <-, <->
web -> api: HTTPS
api -> db: reads/writes
api <-> cache: cached sessions

# Containers group related shapes
cloud: Production VPC {
  api
  db
  cache
}

# Styling is nested under style
api.style: {
  fill: "#eef6ff"
  stroke: "#2b6cb0"
  stroke-width: 3
}
```

Important rules:

- **Keys are not labels.** `be: Backend` creates key `be` with label `Backend`;
  connect with `be -> fe`, not `Backend -> Frontend`.
- **Repeated connections are separate edges.** Target one with `(a -> b)[0]`.
- **Containers are maps.** Nest braces to avoid repeated prefixes; `_` references
  the parent scope.
- **D2 is case-insensitive for keys.** Prefer lowercase snake_case IDs.
- **One hyphen can be part of a key; two hyphens are an edge.** `a-b` is a key,
  `a -- b` is a connection.
- **`d2 validate` only parses.** It passes on source that fails to compile. A
  render is the real check.

## Layout, rendering, and medium

```d2
vars: {
  d2-config: {
    layout-engine: elk
    theme-id: 4
    dark-theme-id: 200
    pad: 40
    center: true
    sketch: false
  }
}
```

- `elk` — orthogonal routing, crossing minimization, better with containers. The
  safer default for anything nontrivial.
- `dagre` — bundled default; fast and compact for small shallow graphs, but
  produces curved wandering routes and handles container children poorly.
- `tala` — when installed: built for software architecture, supports `near`
  another object and `top`/`left` locks.

Render both and compare rather than reasoning about which should win.

```bash
d2 input.d2                              # SVG by default
d2 input.d2 output.png                   # format from the extension
d2 --layout=elk --theme=4 in.d2 out.svg
d2 --watch input.d2 output.svg
d2 --animate-interval=1600 in.d2 out.svg # multi-board as one animated SVG
d2 --target='layers.deployment' in.d2 out.svg
```

Medium changes what the diagram contains, not only how it looks — see
[the layout and medium guide](references/layout-and-medium-guide.md). Briefly:
web docs get SVG plus tooltips; slides get fewer nodes and bigger type; print
gets a legend and no hover; terminal gets ASCII, `elk`, and no color semantics.

Helper scripts:

```bash
scripts/review_d2.py diagram.d2 --dark --png   # engines side by side + contact sheet
scripts/check_d2.sh diagram.d2                 # validate + compile
scripts/render_d2.sh diagram.d2 out.pdf        # render, D2_* env overrides
scripts/scaffold_d2.py create system-architecture arch.d2 --medium slides
scripts/validate_docs.py                       # compile the d2 examples in Markdown
```

## Diagram patterns

Full recipes are in
[the pattern cookbook](references/diagram-pattern-cookbook.md); working starting
points are in `templates/`. The shape of the decision:

| Need | Construct |
|---|---|
| Systems, services, dependencies | containers + classes |
| Ordered interactions over time | `shape: sequence_diagram` |
| Database schema | `shape: sql_table` with row-level edges |
| Class relationships | `shape: class` |
| Pipelines, state machines, decisions | `direction: down` + `shape: diamond` |
| Support matrices, feature tables | `grid-rows` / `grid-columns` |
| Alternate states of one system | `scenarios` |
| An ordered walkthrough | `steps` |
| Drill-down to a different board | `layers` |
| Long text, code, formulas | block strings (`\|md`, `\|latex`, `` \|`ts ``) |

```d2
shape: sequence_diagram
user; browser; api; db

user -> browser: submit form
browser -> api: POST /orders
api -> db: insert order
db -> api: order id
api -> browser: 201 Created
```

```d2
users: {
  shape: sql_table
  id: uuid {constraint: primary_key}
  email: varchar {constraint: unique}
}
orders: {
  shape: sql_table
  id: uuid {constraint: primary_key}
  user_id: uuid {constraint: foreign_key}
}
orders.user_id -> users.id
```

## Before returning a diagram

Score the **rendered image** against
[the visual rubric](references/visual-design-guide.md#9-visual-rubric): message
clarity 25, hierarchy 20, layout and routing 20, typography 15, color and
accessibility 10, consistency 10. Target 80+.

Any of these fails the diagram regardless of score — fix and re-render:

- Overlapping or clipped shapes, labels, or edges
- Text unreadable at the intended viewing size
- Primary direction or reading order ambiguous
- Abstraction levels mixed without the hierarchy being the point
- Color semantics unexplained or inconsistent
- Critical edges lost among low-value ones
- Requires zooming and panning to understand at all
- Light or dark mode renders important content illegible

Then confirm the source-level basics: stable IDs distinct from labels, edges
connected by key, containers that mean something, styling centralized in classes,
and an output format that matches the destination.

If you could not render or inspect the image, do the static review in
[rendering and validation](references/rendering-and-validation.md) and report the
diagram as **statically reviewed but not visually verified**. Do not report a
rubric score for an image you did not see.

## Common fixes

- Edge created duplicate nodes → connect by key, not label.
- Cramped or crossing layout → try `--layout=elk`, add containers, remove
  cross-container edges, flip `direction`.
- Curved wandering edges → switch from `dagre` to `elk`.
- Labels collide → shorten them, drop redundant edge labels, move detail into
  tooltips, or split into boards.
- Diagram is too wide or too tall → flip `direction`, or split the story.
- Text looks small → check `--scale 1` first; SVGs fit to screen by default.
- Dark mode unreadable → drop explicit fills; import `semantic-classes` and set
  `dark-theme-id`.
- `**` glob fails with `"style" needs a value` → it collided with a map inside
  `vars` (such as `d2-config`). Use a single `*`, or put sizes on classes.
- PNG/PDF export fails downloading a browser → render SVG and screenshot it, or
  use `scripts/review_d2.py --png`.
- Import behaves unexpectedly → relative imports resolve from the importing
  file's location.
- `near`, `top`, or `left` ignored → the active layout may not support it.

## References inside this skill

- [Visual design guide](references/visual-design-guide.md) — thesis, hierarchy,
  typography, color, edge hierarchy, density, icons, legends, and the rubric.
- [Layout and medium guide](references/layout-and-medium-guide.md) — the
  render/inspect loop, engine selection, output-medium profiles, multi-board
  storytelling.
- [D2 language reference](references/d2-language-reference.md) — syntax, shapes,
  styles, layouts, special objects, imports, exports.
- [Diagram pattern cookbook](references/diagram-pattern-cookbook.md) —
  architecture, sequence, ERD, UML, pipeline, grid, and composition recipes.
- [Conversion guide](references/conversion-guide.md) — Mermaid, PlantUML,
  Graphviz/DOT, and prose into D2.
- [Rendering and validation](references/rendering-and-validation.md) — install,
  CLI, scripts, CI.
- [Troubleshooting](references/troubleshooting.md) — common mistakes and repairs.
- [Source notes](references/source-notes.md) — research links.
- [Gallery](gallery/) — finished diagrams with design notes, including a
  before/after pair that shows why "it renders" is not enough.
- [Styles](styles/) — the semantic class vocabulary and style packs.
- [Templates](templates/) — starter `.d2` files.
