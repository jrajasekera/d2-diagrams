---
name: d2-diagrams
description: Create, edit, review, validate, render, and troubleshoot D2 declarative diagrams (.d2) for architecture, flowcharts, sequence diagrams, ERDs, UML classes, network/cloud topology, CI/CD, grids, compositions, themes, icons, and documentation exports. Use when the user asks for D2, diagram-as-code, text-to-diagram, SVG/PNG/PDF/PPTX/GIF rendering, or converting Mermaid/PlantUML/Graphviz/whiteboard descriptions into D2.
license: MIT
compatibility: Agent Skills standard. Compatible with Claude Code, Codex, Hermes Agent, and Pi. Optional d2 CLI improves validation/rendering; no network required unless fetching remote icons/images.
metadata:
  version: "1.0.0"
  language: d2
  formats: "svg,png,pdf,pptx,gif,ascii"
---

# D2 Diagrams

Use this skill to create high-quality D2 diagram source, revise existing `.d2` files, convert other diagram descriptions into D2, or render/validate diagrams when the D2 CLI is available.

D2 is a declarative diagram language: describe the system, relationships, containers, styles, and layout hints; let the renderer compute the drawing. Prefer semantic clarity and maintainable source over pixel-perfect placement.

## Core workflow

1. **Identify the diagram job.** Determine the audience, diagram type, required output format, and whether the user wants source only or rendered assets. If details are missing, make a reasonable default rather than stalling: use SVG for documentation, `direction: right` for request/flow diagrams, `direction: down` for pipelines, and minimal styling.
2. **Model before styling.** Name stable IDs first, assign readable labels second, group related nodes into containers, then add edges. Avoid using labels as IDs when the label has spaces or may change.
3. **Choose the diagram pattern.** Use flow/architecture for systems, `shape: sequence_diagram` for ordered interactions, `shape: sql_table` for ERDs, `shape: class` for UML class diagrams, and `grid-rows`/`grid-columns` for matrix layouts.
4. **Use D2 idioms.** Prefer containers over visual swimlanes, classes/globs for repeated styling, themes for broad aesthetics, and imports for shared styles or modular diagrams.
5. **Validate when possible.** If `d2` exists, render to a temporary SVG or requested output. If rendering fails, fix the D2 source before returning. If the CLI is unavailable, perform a careful static review using the checklist below.
6. **Return useful artifacts.** For source requests, provide a `.d2` file or fenced `d2` block. For rendered requests, include the `.d2` source and exported image/document when tools allow.

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
web.shape: rectangle
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
  shadow: true
}
```

Important rules:

- **Keys are not labels.** `be: Backend` creates key `be` with label `Backend`; connect with `be -> fe`, not `Backend -> Frontend`.
- **Repeated connections are separate edges.** Target a specific repeated edge with `(a -> b)[0]`, `(a -> b)[1]`, etc.
- **Containers are maps.** Use nested braces to avoid repeated prefixes. Inside a container, `_` references the parent scope.
- **D2 is case-insensitive for keys.** Prefer lowercase snake_case IDs to avoid ambiguity.
- **One hyphen can be part of a key; two hyphens are an edge.** `a-b` is a shape key, `a -- b` is a connection.

## Choosing layouts and render settings

Use CLI flags when rendering or `vars.d2-config` when settings should live with the diagram.

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

Layout guidance:

- `dagre` is the default and works well for simple directed graphs.
- `elk` is often better for dense hierarchical graphs and many orthogonal relationships.
- `tala`, when installed, is designed for software architecture and supports additional positioning hints such as `near` to another object and `top`/`left` locks.
- Use `direction` for global flow. Avoid manual position controls unless the user needs a specific spatial story.

Render commands:

```bash
# Default SVG output: creates input.svg
d2 input.d2

# Explicit output format from extension
d2 input.d2 output.svg
d2 input.d2 output.png
d2 input.d2 output.pdf
d2 input.d2 output.pptx
d2 input.d2 output.gif
d2 input.d2 output.txt

# Watch mode for iterative editing
d2 --watch input.d2 output.svg

# Layout and theme
d2 --layout=elk --theme=4 input.d2 output.svg
```

Use `scripts/check_d2.sh <file.d2>` to validate by rendering to a temporary SVG, `scripts/render_d2.sh <file.d2> [output]` to render with optional environment overrides, and `scripts/scaffold_d2.py list|create` to copy starter templates.

## Diagram patterns to use

### Architecture / system diagram

Use containers for trust boundaries, cloud accounts, services, regions, subsystems, and deployment units. Keep edges purposeful and labeled with protocols or data types.

```d2
direction: right

client: Customer Browser
edge: CDN / WAF
app: App Cluster {
  web: Web
  api: API
  worker: Worker
}
data: Data Layer {
  db: PostgreSQL { shape: cylinder }
  queue: Queue { shape: queue }
}

client -> edge: HTTPS
edge -> app.web: cached/static
app.web -> app.api: REST
app.api -> data.db: SQL
app.api -> data.queue: jobs
app.worker -> data.queue: consume
app.worker -> data.db: update
```

### Sequence diagram

Use `shape: sequence_diagram` and list participants in intended left-to-right order. In sequence diagrams, declaration order determines vertical order.

```d2
shape: sequence_diagram
user; browser; api; db

user -> browser: submit form
browser -> api: POST /orders
api -> db: insert order
db -> api: order id
api -> browser: 201 Created
browser -> user: confirmation
```

### ERD / SQL tables

Use `shape: sql_table`, field rows, constraints, and row-level foreign key edges.

```d2
users: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  email: varchar { constraint: unique }
  created_at: timestamp
}
orders: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  user_id: uuid { constraint: foreign_key }
  total_cents: int
}
orders.user_id -> users.id
```

### UML classes

Use `shape: class`; fields are keys with type values, methods are keys containing `(`. Prefix fields/methods with `+`, `-`, or `#` for public, private, or protected visibility.

```d2
OrderService: {
  shape: class
  -repo: OrderRepository
  +create_order(user_id string): Order
  +cancel_order(order_id string)
}
OrderRepository: {
  shape: class
  +save(order Order): void
  +find_by_id(id string): Order
}
OrderService -> OrderRepository: uses
```

### Styling with classes and globs

Use classes for reusable semantic styling and globs for broad defaults.

```d2
classes: {
  service: {
    shape: rectangle
    style: {
      fill: "#eef6ff"
      stroke: "#2b6cb0"
      border-radius: 8
    }
  }
  datastore: {
    shape: cylinder
    style: {
      fill: "#fff7ed"
      stroke: "#c2410c"
    }
  }
}

*.style.font-size: 18
*.style.shadow: true

api.class: service
db.class: datastore
api -> db: SQL
```

### Markdown, code, and LaTeX blocks

Use block strings for long text, code, Markdown labels, and formulas.

```d2
note: |md
# Deployment note
- Blue/green release
- Automatic rollback on failed health checks
|

formula: |latex
\frac{d}{dx}x^2 = 2x
|

snippet: |go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
|
```

## Quality checklist

Before returning a diagram, check:

- It answers the user’s actual purpose, not just a generic diagram type.
- IDs are stable, short, and distinct from display labels.
- Every edge has a reason; high-value edges have labels.
- Containers represent meaningful boundaries, not decorative boxes.
- Styles are consistent and mostly centralized through classes, globs, themes, or imports.
- The source is readable, with comments only where they clarify non-obvious choices.
- Output format matches the destination: SVG for web/docs, PNG for raster contexts, PDF/PPTX for presentation documents, GIF/animated SVG for short compositions, ASCII for terminal docs.
- Remote icons/images are acceptable for the user’s environment; otherwise use local paths or omit icons.
- For PNG/PDF/PPTX/GIF exports, note that the D2 CLI may need additional browser/Playwright dependencies.

## Common fixes

- If an edge created duplicate nodes, connect by key, not label.
- If layout is cramped, add containers, reduce cross-container edges, try `direction`, or render with `--layout=elk`.
- If labels collide, shorten labels, move detail into notes/tooltips, or split the diagram into composition boards.
- If imported diagrams behave unexpectedly, remember relative imports resolve from the importing file’s location.
- If `near` to another object or `top`/`left` is ignored, check whether the active layout supports that feature.
- If SVG looks odd in a design tool, view it in a browser; Markdown labels rely on web SVG features.

## References inside this skill

- [D2 language reference](references/d2-language-reference.md) — syntax, shapes, styles, layouts, special objects, imports, exports.
- [Diagram pattern cookbook](references/diagram-pattern-cookbook.md) — architecture, sequence, ERD, UML, pipeline, grid, and composition recipes.
- [Conversion guide](references/conversion-guide.md) — convert Mermaid, PlantUML, Graphviz/DOT, and prose into D2.
- [Rendering and validation](references/rendering-and-validation.md) — install hints, CLI commands, scripts, CI usage, troubleshooting.
- [Troubleshooting](references/troubleshooting.md) — common D2 mistakes and repairs.
- [Source notes](references/source-notes.md) — research links used to author this skill.
- [Templates](templates/) — starter `.d2` files.
