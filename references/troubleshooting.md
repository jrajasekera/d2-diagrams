# D2 troubleshooting guide

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

## PNG/PDF export fails

PNG and PDF exports may need browser dependencies. First validate as SVG:

```bash
d2 diagram.d2 /tmp/diagram.svg
```

Then retry PNG/PDF after installing required browser/Playwright dependencies for the environment.

## Remote icons are missing

Remote icons require network access at render time. Use local files when the render environment is offline:

```d2
service.icon: ./icons/service.svg
```

Or omit icons and rely on labels/shapes.

## Imports cannot be found

Relative imports resolve relative to the importing file, not the shell working directory.

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
