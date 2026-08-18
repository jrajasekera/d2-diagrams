# Visual design guide

The pattern cookbook answers *what structure to use*. This guide answers *how to
make that structure look deliberate*.

A diagram that compiles is not a diagram that works. D2 will happily render tiny
text, twenty crossing edges, six competing colors, and a 4000px-wide strip. The
renderer has no opinion about whether a human can read the result. You do.

Read this before styling anything non-trivial, and again while inspecting a
render.

---

## 1. Start from a visual thesis

Write one sentence — literally write it, in a comment at the top of the `.d2`
file — that states what the diagram is for:

```d2
# Thesis: a customer request crosses the edge layer, is served by the API, and
# only the worker path touches the queue.
```

Then decide four things:

| Decision | Question | Consequence in the source |
|---|---|---|
| **Focal node or path** | What is the viewer supposed to look at first? | `primary_service` / `primary_edge` classes |
| **Reading direction** | Left-to-right request flow? Top-down pipeline? | `direction:` |
| **Primary vs. supporting** | What is context rather than subject? | `secondary_*` classes, lower opacity |
| **What is omitted** | What did you decide *not* to draw? | absence, plus a note saying so |

If you cannot name the focal path, the diagram has no thesis yet and styling it
is premature. Go back to the model.

The thesis is also the acceptance test: after rendering, look at the image for
three seconds and ask whether the thesis is what you see. Not whether it is
*derivable* — whether it is what you see.

---

## 2. Hierarchy

Give every diagram the same predictable ladder, loudest to quietest:

1. **Title** — the diagram's name, if the destination does not already supply one
2. **Boundaries / stages** — containers, trust zones, pipeline phases
3. **Primary components** — the subject of the thesis
4. **Secondary components** — context that must be present but not read first
5. **Edge labels and annotations**
6. **Detail in tooltips, notes, or a linked drill-down board**

Two rules do most of the work:

- **Containers are quieter than their contents.** A boundary is a frame, not a
  participant. Thin stroke, near-white or transparent fill, muted label. The
  `boundary` class in `styles/semantic-classes.d2` encodes this. When a container
  fill is more saturated than the shapes inside it, the frame wins the eye and
  the components disappear.
- **Emphasis comes from contrast and weight, not from a brighter color.** Promote
  a node with a heavier stroke (`stroke-width: 3`), bolder label, or slightly
  larger size — the same accent hue as the rest of its family. Reaching for a new
  color to mean "important" is how diagrams end up with six meanings and no
  hierarchy.

De-emphasis is the underused half. `style.opacity: 0.45` on context nodes is
often more effective than emphasizing the focus, because it removes competition
instead of adding noise.

---

## 3. Typography

Pick a scale before you pick sizes. D2 accepts `font-size` from 8 to 100; these
are documentation-scale starting points, to be shifted up as a block for
presentation and down for dense reference diagrams:

| Role | `font-size` |
|---|---|
| Diagram title | 28–36 |
| Major boundary / stage labels | 20–24 |
| Primary components | 16–20 |
| Secondary components | 14–18 |
| Edge labels, annotations | 12–15 |

Rules:

- **Three tiers among the shapes.** Boundary labels and edge labels are separate
  registers and sit outside that count, so an ordinary diagram lands on four or
  five distinct sizes in total — the bundled packs use 14/16/18 for shapes, 22
  for boundaries, and 14 for every edge label.
- **Make the steps large enough to be intentional.** Two sizes 1–2px apart read
  as a mistake, not a hierarchy. If two things need distinguishing but not
  ranking, use weight or color, not a 1px size difference.
- **One size for all edge labels.** Edge importance is carried by stroke weight
  and dash; varying the label size too is a second signal for the same
  distinction, and it makes the diagram look unfinished.
- **One or two lines per node label.** A three-line label means the node is doing
  too much; split it, or move the detail into a tooltip.
- **Concise nouns for components, short verbs or protocols for edges.**
  `Order Service` and `gRPC`, not `The service that handles orders` and
  `sends a request to over gRPC`.
- **Set sizes on classes, not on nodes.** `classes.primary_service.style.font-size`
  keeps the scale in one place; a per-node `font-size` is a local exception you
  will forget you made.

Avoid the recursive glob `**.style.font-size` as a shortcut for "make everything
bigger": it collides with `vars` (see
[troubleshooting](troubleshooting.md#style-needs-a-value-from-a-glob-line)) and it
flattens the hierarchy you just built.

Custom fonts are available via CLI flags (`--font-regular`, `--font-bold`,
`--font-semibold`, `--font-italic`, `--font-mono` and their mono variants), which
`scripts/render_d2.sh` exposes as `D2_FONT_*` environment variables. Use them for
brand alignment, and remember the fonts must exist wherever the diagram is next
rendered — a `.d2` file cannot carry them.

---

## 4. Color

Restraint is the entire technique. A four-family palette covers almost every
technical diagram:

| Family | Meaning | Rule |
|---|---|---|
| **Neutral** | ordinary infrastructure, context, boundaries | the default; most shapes live here |
| **Accent** (one) | the primary subject and the primary flow | one hue family, used sparingly |
| **Data** | datastores, queues, caches — anything that holds state | a second hue, distinct from the accent |
| **Status** | red / amber / green | reserved, never decorative |

Status colors are load-bearing and must not be spent on anything else:

- **Red** — failure, outage, critical risk, data loss
- **Amber** — warning, manual gate, approval, degraded, needs attention
- **Green** — success, healthy, completed

If a diagram uses green for "the frontend" and red for "the database," a reader
who scans for problems finds a false one. Pick the accent and data families from
outside red/amber/green so the semantics stay available.

**Never let color be the only encoding.** Roughly 1 in 12 men has some form of
color vision deficiency, and diagrams get printed, photocopied, and pasted into
grayscale decks. Every color distinction needs a redundant cue:

| Distinction | Color | Redundant cue |
|---|---|---|
| datastore vs. service | teal vs. indigo | `shape: cylinder` vs. `rectangle` |
| async vs. sync edge | teal vs. indigo | `stroke-dash: 4` |
| failure path | red | label (`timeout`), dashed stroke |
| healthy vs. degraded vs. down | green / amber / red | solid vs. dashed vs. double border |
| external system | grey | dashed border, `person`/dashed rectangle |

The bundled style packs are built this way: shape, dash, and stroke weight carry
the meaning, and color reinforces it. `styles/semantic-classes.d2` alone —
imported with no palette — is a complete, legible diagram vocabulary. That is the
test of whether color is doing too much work.

The status classes are the ones this matters most for, because they are what a
reader scans for, so they get a border treatment as well as a hue: `success` is
solid, `warning` is dashed, `failure` is a double border. Told apart in
greyscale, they still read correctly.

Two colors are deliberately shared. `decision` and `warning` are both amber
because amber covers the whole "needs attention" register — a manual gate and a
degraded component are the same signal to a reader — and they are told apart by
shape. `fallback_edge` is amber for the same reason and is told apart by being an
edge. Sharing a hue across things that mean the same thing is not a collision;
sharing one across things that do not is.

Two further notes:

- **Dark mode.** Explicit `fill`/`stroke` values override the dark theme, so a
  hand-colored light diagram becomes unreadable dark-on-dark. For one file that
  follows the viewer, import `styles/semantic-classes.d2` (no colors) and set
  `theme-id` plus `dark-theme-id`. Use `styles/minimal-dark.d2` only when the
  destination is known to be dark.
- **Themes first, hex second.** D2 ships professionally designed themes
  (`d2 themes`) plus `theme-overrides` / `dark-theme-overrides`. Start from a
  theme and override the handful of semantic colors you need. Hand-coloring every
  object is how a diagram acquires a palette nobody chose.

---

## 5. Edge hierarchy

Edges decide whether an architecture diagram reads as a system or as a hairball.
Nodes are easy; edges are where diagrams fail.

Defaults, all available as classes in `styles/semantic-classes.d2`:

| Relationship | Treatment |
|---|---|
| Primary flow | solid, heavier stroke (3–5), accent color, labeled |
| Secondary dependency | solid, thin stroke (1), neutral color |
| Asynchronous / eventual | `stroke-dash: 4`, data-family color |
| Failure / fallback | `stroke-dash: 3`, amber or red, **always labeled** |
| Optional / weak | `style.opacity: 0.4` |

Discipline that matters more than the styling:

- **Every edge must earn its place.** "These two things are related" is not a
  reason. If removing an edge does not change what the reader concludes, remove
  it.
- **Bidirectional arrows (`<->`) only for genuinely symmetric relationships.**
  Request/response is not symmetric — it is one arrow labeled with the call.
  A diagram full of `<->` has given up on describing direction.
- **Do not cross a major boundary to show a low-value dependency.** One edge from
  a deep container child to a far-away node forces the layout engine to route
  around everything. Either promote the relationship (it is important enough to
  restructure for) or drop it.
- **Label the high-value edges, not all of them.** Ten labeled edges is ten
  labels competing; three labeled edges among ten is a legible emphasis.

If several edges converge on one node, give that node more room — `width` and
`height` on a highly connected shape hand the layout engine routing surface it
otherwise has to steal from neighbors.

---

## 6. Density and whitespace

Heuristics, not limits:

- **12–15 primary nodes** is a comfortable documentation diagram.
- **Past ~20 total nodes**, actively consider splitting the view rather than
  proceeding.
- **One abstraction level per board.** A diagram that shows both "Payments
  Service" and "`retry_policy.go`" has no consistent zoom, and the reader cannot
  tell which level is the point. Mixing levels is legitimate only when the
  hierarchy itself is the subject.
- **Collapse repetition.** Three identical app nodes become one labeled
  `App Node (×3)`, or one container. Drawing the third one adds no information.
- **Move trivia out, not down.** Version numbers, instance counts, config flags,
  and caveats belong in a `tooltip`, a Markdown `note` shape, a `link` to a
  drill-down board, or a separate layer — not in a node label.

The failure mode to name explicitly: **do not solve crowding by shrinking text or
adding colors.** Both make the diagram worse in exchange for fitting. Split the
visual story into boards instead (see
[layout and medium guide](layout-and-medium-guide.md#multi-board-storytelling)).

Whitespace is a design element and is mostly controlled by `pad` (outer margin,
default 100), by how many nodes you asked for, and by container structure. If a
render feels cramped, the usual cause is too many nodes or too many
cross-container edges, not a padding setting.

---

## 7. Icons

Icons are the fastest way to make a diagram look either professional or like a
clip-art collage. The difference is a policy, applied consistently.

- **One coherent family.** Never mix filled, outline, flat, and photographic
  assets in one diagram. Pick a set and stay in it.
- **Provider icons where provider identity matters** — an AWS/GCP/Azure topology
  where "which managed service" is the point. Otherwise shapes carry more
  information per pixel.
- **Conceptual icons only when recognition beats reading.** A database cylinder
  or a lock is faster than its label. A generic gear is not.
- **Not on every node.** Icons on all shapes is the same mistake as bolding every
  word. Consider icons for one category (external providers, say) and shapes for
  the rest.
- **Prefer local paths when reproducibility matters.** Remote icon URLs make the
  render depend on the network and on someone else's uptime; a CI run or an
  offline agent will produce a different image. Check whether the environment
  allows remote fetches before using them.
- **The diagram must survive icon removal.** If deleting the icons makes the
  diagram ambiguous, the labels are doing too little.

D2 places icons automatically, supports icons on connections, and accepts both
local files and URLs — see
[the language reference](d2-language-reference.md) for syntax.

---

## 8. Legends

A legend is required whenever the diagram's visual encoding is not
self-evident — which is most of the time once you are using an edge hierarchy.

Use D2's native legend rather than hand-built boxes: it explains objects and
connections together and lays itself out.

```d2
...@../styles/minimal-light

api: API {class: primary_service}
db: Store {class: datastore}
api -> db: SQL {class: primary_edge}

vars: {
  d2-legend: {
    svc: Service {class: primary_service}
    store: Stateful store {class: datastore}
    svc -> store: Synchronous call {class: primary_edge}
    svc -> store: Asynchronous / eventual {class: async_edge}
    store -> svc: Failure path {class: fallback_edge}
  }
}
```

Two things the syntax will not tell you, both of which produce a legend that
looks broken rather than an error:

- **Sample connections must reuse keys already declared inside the legend.**
  Every key under `d2-legend` becomes an entry, so demonstrating an edge style
  with a throwaway `l1 -> l2` silently adds `l1` and `l2` as their own swatches.
  Draw the samples between the objects you already listed; repeating a pair is
  fine, which is why `svc -> store` appears twice above.
- **The heading is always "Legend".** There is no custom-title key; a `title:`
  entry just becomes another labelled swatch.

Use `class:` inside the legend rather than copying hex values. That keeps the
legend honest — it shows the styles the diagram actually uses, instead of an
approximation that drifts the next time the palette changes.

A legend matters most in print and PDF, where there are no tooltips to fall back
on, and is noise when a diagram uses only one kind of edge.

---

## 9. Visual rubric

Score the *rendered image*, not the source. Target **80+ with no hard failures**.
Use it to drive revisions, not to decorate a finished answer.

| Area | Points | Question |
|---|---:|---|
| Message clarity | 25 | Is the intended takeaway obvious in about three seconds? |
| Visual hierarchy | 20 | Does the eye know where to start and what matters? |
| Layout and routing | 20 | Are flow, spacing, crossings, and aspect ratio effective? |
| Typography | 15 | Is all text legible at the destination size? |
| Color and accessibility | 10 | Is color restrained, meaningful, and redundant with other cues? |
| Consistency and finish | 10 | Are sizes, shapes, icons, strokes, and labels coherent? |

### Hard failures

Any one of these fails the diagram regardless of score. Fix and re-render.

- Overlapping or clipped shapes, labels, or edges
- Text unreadable at the intended viewing size
- Primary direction or reading order is ambiguous
- Abstraction levels mixed without the hierarchy being the point
- Color semantics unexplained or used inconsistently
- Critical edges lost among low-value ones
- The diagram requires zooming and panning to understand at all
- Light or dark mode renders important content illegible

### Scoring notes

- **25 points on message clarity** is deliberate: a beautiful diagram of the
  wrong thing scores 55.
- Judge typography at the destination size. SVGs scale to fit their container by
  default, so "the text looks small" in a fit-to-window preview is often a
  viewport artifact — render with `--scale 1` (or `D2_SCALE=1`) before believing
  it, and conversely check a wide diagram at the width it will actually occupy.
- If you could not render or inspect the image, say so: report the diagram as
  **statically reviewed but not visually verified**, and do not report a rubric
  score you did not observe.

---

## 10. Revision moves

When a render fails the rubric, these are the actual levers, cheapest first:

| Symptom | Moves |
|---|---|
| Too wide / bad aspect ratio | flip `direction`, group into containers, split into boards |
| Many edge crossings | switch to `elk`, reorder declarations, promote a hub node's size, remove low-value edges |
| Curved, wandering edges | switch from `dagre` to `elk` for orthogonal routing |
| Labels collide | shorten labels, drop redundant edge labels, move detail to tooltips |
| No focal path | apply `primary_edge`/`primary_service`, drop opacity on context |
| Feels cluttered but nothing is wrong | count nodes; you are probably past 20 |
| Container dominates its contents | quiet the container (`boundary` class), not the children |
| One node is a routing bottleneck | give it explicit `width`/`height` |
| Colors fight | collapse to neutral + one accent + data + status, re-check status usage |
| Unreadable in dark mode | drop explicit fills, import `semantic-classes` + `dark-theme-id` |

Prefer structural moves (fewer nodes, better containers, different layout engine)
over cosmetic ones (smaller font, more color). Cosmetic fixes hide the problem;
structural fixes remove it.

---

## Related

- [Layout and medium guide](layout-and-medium-guide.md) — engine selection, the
  render/inspect loop, and output-medium profiles.
- [Diagram pattern cookbook](diagram-pattern-cookbook.md) — what structure to use
  for each diagram type.
- [D2 language reference](d2-language-reference.md) — the syntax behind every
  attribute named here.
- `styles/` — the bundled style packs that implement this guide.
