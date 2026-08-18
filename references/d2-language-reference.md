# D2 language reference for agents

This is a compact operational reference for authoring D2 diagrams. It emphasizes patterns that agents commonly need when generating, revising, or debugging `.d2` source.

## Mental model

D2 source is a map of objects and attributes. Objects can be shapes, containers, connections, classes, boards, or special objects. The renderer uses a layout engine to turn that semantic model into a diagram.

Write diagrams in this order:

1. Configuration: `vars.d2-config`, `direction`, broad globs.
2. Reusable styling: `classes` and shared objects.
3. Domain objects: nodes, containers, tables, participants.
4. Relationships: edges with labels.
5. Targeted refinements: styles, dimensions, tooltips, links, icons.

## Shapes

Basic declaration:

```d2
api
api: API Gateway
api.shape: rectangle
```

Common shape values:

```text
rectangle, square, page, parallelogram, document, cylinder, queue,
package, step, callout, stored_data, person, diamond, oval, circle,
hexagon, cloud, c4-person
```

Special shape values:

```text
sql_table, class, sequence_diagram, image, text
```

Notes:

- Default shape is `rectangle`.
- `circle` and `square` preserve a 1:1 aspect ratio.
- Keys are case-insensitive. Use lowercase snake_case IDs for consistency.
- Use labels for display text and keys for references.

## Labels, keys, strings

```d2
be: Backend
fe: Frontend
be -> fe: calls
```

Do not connect labels accidentally:

```d2
# Bad: creates separate shapes named Backend and Frontend
Backend -> Frontend

# Good
be -> fe
```

Use quotes when a key or value would otherwise collide with syntax/reserved words:

```d2
my_table: {
  shape: sql_table
  "label": string
}
```

## Connections

Operators:

```d2
a -- b      # undirected line
a -> b      # directed from a to b
a <- b      # directed from b to a
a <-> b     # bidirectional
```

Labels:

```d2
frontend -> backend: HTTPS
```

Repeated connections create distinct edges:

```d2
db -> s3: backup
db -> s3: restore
(db -> s3)[0].style.stroke: green
(db -> s3)[1].style.stroke: orange
```

Connection chaining:

```d2
client -> cdn -> web -> api -> db
```

Arrowheads:

```d2
orders.user_id -> users.id: {
  target-arrowhead.shape: cf-one-required
  source-arrowhead.shape: cf-many
}
```

Common arrowhead shapes include `triangle`, `arrow`, `diamond`, `circle`, `box`, `cf-one`, `cf-one-required`, `cf-many`, `cf-many-required`, and `cross`.

## Containers

Containers group objects. They are useful for cloud accounts, regions, services, modules, domains, trust boundaries, and layers.

```d2
prod: Production {
  web -> api
  api -> db
}
```

Alternative label form:

```d2
prod: {
  label: Production
  web
  api
}
```

Nested containers:

```d2
clouds: {
  aws: {
    lb -> api -> db
  }
  gcp: {
    auth -> users
  }
  gcp.auth -> aws.api: token introspection
}
```

Reference parent with `_`:

```d2
frontend: {
  ui
  ui -> _.backend.api: calls
}
backend: {
  api
}
```

## Styles

Styles live under `style`.

```d2
api.style: {
  opacity: 0.95
  stroke: "#2563eb"
  fill: "#eff6ff"
  fill-pattern: dots
  stroke-width: 2
  stroke-dash: 3
  border-radius: 8
  shadow: true
  font-size: 18
  font-color: "#172554"
  bold: true
}
```

Common style keys:

```text
opacity, stroke, fill, fill-pattern, stroke-width, stroke-dash,
border-radius, shadow, 3D, multiple, double-border, font, font-size,
font-color, animated, bold, italic, underline, text-transform, root
```

Use transparent fill:

```d2
legend.style.fill: transparent
```

## Classes

Classes aggregate reusable attributes.

```d2
classes: {
  service: {
    shape: rectangle
    style: {
      fill: "#eef6ff"
      stroke: "#2563eb"
    }
  }
  unhealthy: {
    style: {
      fill: "#fee2e2"
      stroke: "#dc2626"
    }
  }
}

api.class: service
worker.class: [service; unhealthy]
```

Connection classes:

```d2
a -> b: { class: async }

# Or target a specific existing edge
a -> b
(a -> b)[0].class: async
```

When multiple classes are applied, order matters: later classes can override earlier ones.

## Globs

Globs make broad changes.

```d2
*.style.font-size: 18
*.style.shadow: true
```

Recursive globs:

```d2
**.style.stroke-width: 2
```

Filters:

```d2
*: {
  &shape: cylinder
  style.fill: "#fff7ed"
}

*: {
  &class: service
  style.border-radius: 8
}
```

Global triple globs persist across nested layers and imports:

```d2
***.style.font-size: 16
```

Use globs carefully. They are powerful, but excessive global rules can make a diagram difficult to reason about.

## Dimensions and positioning

```d2
api.width: 160
api.height: 80
```

Most shapes support `width` and `height`; containers usually resize to fit children.

Use `near` for diagram titles, legends, and explanatory notes:

```d2
title: System Overview {
  shape: text
  near: top-center
  style.font-size: 32
}
```

Label and icon positioning:

```d2
worker.label.near: outside-bottom-center
worker.icon.near: top-left
```

TALA-specific positioning features include `near` to another object and `top`/`left` locks. Do not rely on those unless TALA is available.

## Text, Markdown, code, and LaTeX

Block string format:

```d2
note: |md
# Heading
- Markdown content
|
```

Markdown label on a shape requires explicit shape declaration:

```d2
note: |md
# Important
This is rendered as Markdown inside a rectangle.
|
note.shape: rectangle
```

Code blocks use language names or aliases:

```d2
handler: |ts
export async function handler(req: Request) {
  return new Response("ok")
}
|
```

Aliases include `md`, `tex`, `js`, `go`, `py`, `rb`, and `ts`.

LaTeX / MathJax:

```d2
formula: |latex
\lim_{h \to 0} \frac{f(x+h)-f(x)}{h}
|
```

If the content itself contains pipes, use a different delimiter:

```d2
code: |`ts
declare function getSmallPet(): Fish | Bird;
const ok = a || b;
`|
```

## Icons and images

<!-- validate:skip -->
```d2
server: {
  shape: image
  icon: https://icons.terrastruct.com/tech/022-server.svg
}

deploy: {
  icon: ./icons/deploy.svg
}
```

Remote icons require network access at render time. Local images work with the CLI when the path is resolvable from the diagram file.

## SQL tables

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
}

orders.user_id -> users.id
```

Recognized constraints are shortened in the table display, including `primary_key`, `foreign_key`, and `unique`. Multiple constraints can use arrays:

```d2
accounts: {
  shape: sql_table
  email: varchar { constraint: [unique; not_null] }
}
```

## UML classes

```d2
Cart: {
  shape: class
  +items: "[]CartItem"
  +add(item CartItem): void
  +total(): Money
}
```

Visibility prefixes:

```text
none or +  public
-          private
#          protected
```

A key containing `(` is a method; the value is the return type. If no return type is given, it represents void.

## Sequence diagrams

Root-level sequence diagram:

```d2
shape: sequence_diagram
user; web; api; db
user -> web: click Buy
web -> api: POST /orders
api -> db: insert
db -> api: id
api -> web: 201
web -> user: success
```

Nested sequence diagram as an object:

```d2
login_flow: {
  shape: sequence_diagram
  browser; auth; users
  browser -> auth: login
  auth -> users: verify password
  users -> auth: ok
  auth -> browser: session cookie
}
```

Sequence-specific rules:

- Actor declaration order determines left-to-right order.
- Connection declaration order determines top-to-bottom sequence.
- Children of a sequence diagram share scope across groups.
- Groups are containers inside the sequence diagram.
- Notes are nested objects on an actor with no connections.
- Self messages are valid: `api -> api: validate`.

## Grid diagrams

```d2
grid-columns: 3
grid-gap: 30
linux; macos; windows
x86; arm64; riscv
```

Use `grid-rows`, `grid-columns`, `grid-gap`, `vertical-gap`, and `horizontal-gap`. When both rows and columns are set, the first one defined determines fill order.

## Variables and substitutions

```d2
vars: {
  env: prod
  colors: {
    service: "#eef6ff"
  }
}

api: API ${env}
api.style.fill: ${colors.service}
```

Single quotes bypass substitutions:

```d2
msg: 'literal ${env}'
```

Spread substitutions work for maps and arrays:

```d2
vars: {
  base_style: {
    fill: "#eef6ff"
    stroke: "#2563eb"
  }
}
api.style: {
  ...${base_style}
  shadow: true
}
```

## Themes and config variables

CLI:

```bash
d2 --theme=4 --dark-theme=200 input.d2 output.svg
```

In-source config:

```d2
vars: {
  d2-config: {
    theme-id: 4
    dark-theme-id: 200
    layout-engine: elk
    pad: 40
    center: true
    sketch: true
  }
}
```

CLI flags and environment variables take precedence over `vars.d2-config`.

## Layouts

Common layout engines:

- `dagre`: default, fast, directed layered layouts.
- `elk`: directed layout, often more mature for dense hierarchical diagrams.
- `tala`: software architecture-oriented engine with D2-specific features, if installed.

Set layout:

```bash
d2 --layout=elk input.d2 output.svg
D2_LAYOUT=elk d2 input.d2 output.svg
```

Set direction:

```d2
direction: right
```

Direction values: `up`, `down`, `right`, `left`.

## Imports

Regular import:

<!-- validate:skip -->
```d2
# styles.d2 contains classes, globs, etc.
styles: @styles
```

Spread import inside a map:

<!-- validate:skip -->
```d2
...@common-style
```

Partial import:

<!-- validate:skip -->
```d2
admin: @people.admin
```

Rules:

- D2 imports `.d2` files; the extension can be omitted.
- Relative imports resolve relative to the importing file, not the shell working directory.
- Use quoted imports for file names containing dots: `@"schema-v0.1.2"`.
- Spread imports insert the imported map contents into the current map.

## Composition: layers, scenarios, steps

Composition creates multiple boards from one source.

```d2
client -> api -> db

scenarios: {
  outage: {
    db.style.opacity: 0.25
    api -> replica: failover
  }
}
```

Board types:

- `layers`: independent boards that do not inherit from the root.
- `scenarios`: alternate views that inherit from the base layer.
- `steps`: sequential boards; each step inherits from the previous step.

Useful outputs for compositions: animated SVG (`--animate-interval=1200`), GIF, PDF, and PPTX.

## Exports

The CLI can export `.d2` to SVG, PNG, PDF, PPTX, GIF, ASCII text, or stdout. SVG is the default when no output file is specified.

```bash
d2 in.d2          # creates in.svg
d2 in.d2 out.svg
d2 in.d2 out.png
d2 in.d2 out.pdf
d2 in.d2 out.pptx
d2 in.d2 out.gif
d2 in.d2 out.txt
```

Stdout:

```bash
echo 'x -> y' | d2 - - > out.svg
```
