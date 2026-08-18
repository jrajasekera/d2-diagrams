# D2 troubleshooting guide

Compile-time problems come first; the visual problems that a successful render
hides come after them. Both kinds are real bugs.

## Duplicate unexpected nodes

Symptom: The render has both `Backend` and `be: Backend` as different nodes.

Cause: Edges referenced labels instead of keys.

Fix:

```d2
be: Backend
fe: Frontend

# Bad
Backend -> Frontend

# Good
be -> fe
```

## Connection styles affect the wrong edge

Symptom: Styling `(a -> b)[0]` changes a different edge than expected.

Cause: Repeated edges are indexed in declaration order.

Fix: Keep repeated connections together and comment them.

```d2
a -> b: backup
# first repeated edge
(a -> b)[0].style.stroke: green

a -> b: restore
# second repeated edge
(a -> b)[1].style.stroke: orange
```

## Diagram is too tangled

Try, in order:

1. Add meaningful containers.
2. Remove low-value edges.
3. Label only important edges.
4. Change `direction`.
5. Render with `--layout=elk`.
6. Split into multiple diagrams or composition boards.
7. Use `near` for legends/notes rather than forcing positions.

## Containers are not sizing as expected

Containers resize to children. Do not rely on `width`/`height` for containers across all layout engines. Apply dimensions to shapes, or add explanatory text/legend if the container needs visual balance.

## `near`, `top`, or `left` did not work

Some positioning features are layout-specific. `near` to constants works broadly, while `near` to another object and `top`/`left` are TALA-specific. Use a supported layout or fall back to semantic layout hints.

## Markdown or code label does not render as expected

For Markdown labels on a shape, explicitly declare the shape:

```d2
note: |md
# Heading
|
note.shape: rectangle
```

If block contents include pipes, use a custom delimiter:

```d2
code: |`ts
const ok = a || b;
type Result = A | B;
`|
```

## `d2 validate` passed but the render failed

`d2 validate` only parses. Unresolved keys, indexed edges that do not exist,
missing imports, and unbundlable local icons all pass validation and then fail to
compile. A render is the real check; `scripts/check_d2.sh` does both.

## `"style" needs a value` from a glob line

Symptom: a line like `**.style.font-size: 16` fails with
`"style" needs a value`, sometimes pointing at an imported file.

Cause: the recursive glob `**` matched a *map* inside `vars` — `vars.d2-config`,
say — where `style` is not a valid key. A `**` glob alongside only scalar `vars`
compiles fine; it is the nested map that breaks it. Since any diagram setting a
layout engine or theme in source has `vars.d2-config`, in practice the two rarely
coexist.

Fix: use the single-level `*` glob, or — better — put type sizes on classes,
which is what the bundled style packs do:

```d2
classes: {
  primary_service: {
    style.font-size: 18
  }
}

api: API {class: primary_service}
```

## d2 crashes with a goroutine stack overflow

Symptom: `d2` dies with a Go runtime `stack overflow` dump instead of an error
message.

Cause (seen on 0.7.1): a `**` recursive glob whose value is a variable
substitution, e.g. `**.style.fill: ${primary}`. The glob and the substitution
recurse into each other.

Fix: do not combine `**` with `${...}`. Set the value literally, or apply it
through a class. This is another reason the bundled packs put style values on
classes rather than on glob lines.

## PNG/PDF/PPTX export fails downloading a browser

Symptom: `got non 200 status code: 404 ... playwright ... .zip`, a network
timeout, or a hang, and no output file.

Cause: D2's raster pipeline downloads a Playwright browser on first use. Offline
environments, sandboxes, and restricted CI cannot fetch it.

Fix: render SVG (which needs nothing) and screenshot it with a browser that is
already installed:

```bash
d2 diagram.d2 /tmp/diagram.svg
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars \
  --window-size=1800,1200 --screenshot=/tmp/diagram.png /tmp/diagram.svg
```

`scripts/review_d2.py --png` tries D2 first and falls back to this automatically.

## Remote icons are missing

Remote icons require network access at render time. Use local files when the render environment is offline:

<!-- validate:skip -->
```d2
service.icon: ./icons/service.svg
```

Or omit icons and rely on labels/shapes.

## Imports cannot be found

Relative imports resolve relative to the importing file, not the shell working directory.

<!-- validate:skip -->
```d2
# In diagrams/app/main.d2, this reads diagrams/styles/common.d2
...@../styles/common
```

D2 only opens `.d2` imports. The extension can be omitted, and the formatter may omit it.

## A shape name with punctuation behaves strangely

Use stable IDs and labels:

```d2
# Better than using the whole label as an ID
api_gateway: API Gateway (public)
```

Use quotes when needed:

```d2
"service.v1": Service v1
```

## Globs changed too much

Limit scope or add filters:

```d2
# Broad
*.style.fill: "#eef6ff"

# More targeted
*: {
  &class: service
  style.fill: "#eef6ff"
}
```

Prefer classes for semantic reusable styling.

## The diagram is pixel-perfect in the user's head

D2 is best when the layout can be automated from semantic constraints. Explain briefly if needed and provide the closest maintainable representation. For exact artistic placement, a design tool may be more appropriate, but D2 can still provide a clear source-controlled model.

## The legend has entries nobody asked for

Symptom: `vars.d2-legend` shows swatches labelled `l1`, `l2`, or a stray entry
named after your intended title.

Cause: every key inside `d2-legend` becomes an entry. Writing `l1 -> l2` to
demonstrate an edge style silently creates two objects, and there is no
custom-title key — the heading is always "Legend", so a `title:` entry just
becomes another swatch.

Fix: draw the sample connections between the objects the legend already lists.
Repeating a pair is fine.

```d2
a: Service
b: Store {shape: cylinder}
a -> b

vars: {
  d2-legend: {
    svc: Service {style.stroke: "#4f46e5"}
    store: Stateful store {shape: cylinder; style.stroke: "#0f766e"}
    svc -> store: Synchronous {style.stroke: "#4f46e5"; style.stroke-width: 3}
    svc -> store: Asynchronous {style.stroke-dash: 4; style.stroke: "#0f766e"}
  }
}
```

## Dark mode renders the diagram unreadable

Symptom: `dark-theme-id` is set, but the dark render is the light diagram on a
dark background — or identical to the light one.

Cause: explicit `fill` and `stroke` values override the theme. A hand-colored
light diagram cannot adapt.

Fix: import `styles/semantic-classes.d2`, which carries shape, stroke weight,
dash, and type size but no colors, and let the theme supply the palette:

```d2
...@../styles/semantic-classes

vars: {
  d2-config: {
    theme-id: 0
    dark-theme-id: 200
  }
}

api: API {class: primary_service}
db: Store {class: datastore}
api -> db: SQL {class: primary_edge}
```

`scripts/review_d2.py --dark` warns when the two renders share most of their
palette, which is how this gets caught.

## The text looks too small

Check `--scale 1` before changing any `font-size`. SVG output fits to its
container by default, so a wide diagram viewed in a browser window or a
screenshot shows uniformly small text even when the type is 26px:

```bash
d2 --scale 1 diagram.d2 /tmp/diagram.svg
```

If it is legible at true size, the problem is the diagram's width relative to its
destination, not its typography. Fix the width — flip `direction`, group into
containers, or split into boards.

## Everything is the same visual weight

Symptom: the diagram is correct, compiles, and reads as an undifferentiated mass
of boxes.

Cause: no edge hierarchy and no focal path. Twenty identical arrows means the
request path and a metrics scrape look equally important.

Fix: apply the style packs' edge classes — `primary_edge` for the focal path,
`secondary_edge` for dependencies, `async_edge` for queued work,
`fallback_edge` for failure — and drop context nodes to `style.opacity: 0.45`.
De-emphasising the surroundings usually beats emphasising the subject. See
[the visual design guide](visual-design-guide.md#5-edge-hierarchy).

## Color is doing too much work

Symptom: five or six fill colors, and a reader cannot say what any of them means.

Fix: collapse to neutral, one accent, one data family, and status. Keep red,
amber, and green exclusively for failure, warning, and success — if they are
spent decoratively there is no color left to signal a real problem. Then check
that every color distinction has a redundant cue (shape, dash, stroke weight, or
the label), because the diagram will be printed, screenshotted in grayscale, and
read by someone with a color vision deficiency.
