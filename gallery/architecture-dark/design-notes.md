# architecture-dark — adaptive light/dark

**Brief.** "The same platform diagram, for our docs site — it has a dark mode and
the current diagram is unreadable in it."

**Thesis.** A read request is served entirely from the cache tier; only writes
reach Postgres.

**Style pack / engine / medium.** `semantic-classes` · elk · docs site with a
dark mode.

**Focal path.** `client → api.read → cache` for reads and
`client → api.write → db` for writes: two parallel paths, both `primary_edge`,
which is the point — the diagram is about the split.

**Deliberately omitted.** Cache key strategy, TTLs, the stampede protection, and
the CDN's own origin config. All of them are cache-design questions; this board
answers "what talks to what".

### The one design decision that matters here

It imports `styles/semantic-classes.d2`, which has **no colors at all**, and sets
`theme-id: 0` with `dark-theme-id: 200`.

Explicit `fill` and `stroke` values override D2's dark theme. A diagram
hand-colored for light mode does not "adapt" — it renders its light fills on a
dark background and becomes unreadable. So for anything that must follow the
viewer, the palette has to come from the theme, and the diagram's own vocabulary
has to be carried by things a theme does not touch: **shape** (cylinder vs.
rectangle), **stroke weight** (primary vs. secondary), and **dash** (sync vs.
async).

That is the honest test of whether color was doing too much work. This diagram is
fully legible in a single hue.

`scripts/review_d2.py --dark` will tell you when you have got this wrong: it
compares the two renders' palettes and warns when the dark one is just the light
one on a dark background.

### The failure mode this example exists to catch

Importing `minimal-light` and setting `dark-theme-id` *looks* correct in source.
It compiles, the flag is spelled right, and nothing warns you — but the explicit
fills win and both renders come out identical. The only way to notice is to look
at both, which is what `review_d2.py --dark` automates.
