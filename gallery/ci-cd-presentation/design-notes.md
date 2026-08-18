# ci-cd-presentation — designed for a projector

**Brief.** "One slide for the engineering all-hands: why our deploys are safe."

**Thesis.** Nothing reaches production without passing an automated gate, and a
failing canary rolls itself back.

**Style pack / engine / medium.** `presentation` · dagre · 16:9 slide.

**Focal path.** `merge → pipeline → canary → rollout`, straight down the middle
of the slide at stroke-width 5.

**Deliberately omitted.** Every stage of the actual pipeline. There is no lint
step, no SBOM, no staging environment, no artifact registry. The docs version of
this diagram has eleven nodes; this one has five.

### Why five nodes

An all-hands audience gets about ten seconds and cannot zoom. The constraint is
not screen size, it is attention. The usual failure is to take the docs diagram
and shrink the type until it fits — which produces a slide nobody reads and
everybody nods at.

Concretely, `presentation` differs from `minimal-light` by:

- one full type tier larger everywhere (26px primary nodes vs. 18px)
- `stroke-width` 5 on the primary path instead of 3
- stronger fills — subtlety does not survive a projector
- `pad: 80` instead of 40

**Red appears exactly once**, on the one box that means "something went wrong",
and green exactly once on the outcome. That is the entire color argument of the
slide, readable from the back of the room.

### The trap this example exists to warn about

The obvious move is to take the eleven-node docs pipeline and swap
`...@minimal-light` for `...@presentation`. That makes it *worse*. Bigger type on
the same node count produces a wider diagram, the slide scales the whole thing
down to fit, and the text ends up looking exactly as small as before — with less
of it visible.

Changing the style pack without changing the node count does nothing. The medium
changes what the diagram should *contain*, not just how it looks.
