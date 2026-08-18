# event-driven-editorial — a diagram that belongs in an article

**Brief.** "A diagram for the blog post *We deleted our service mesh*. It should
look like it belongs in the article, not in a Confluence page."

**Thesis.** Replacing synchronous service-to-service calls with one event topic
removed every cross-service dependency.

**Style pack / engine / medium.** `editorial` · elk · blog post, ~800px column.

**Focal path.** `orders → order.events`, then the fan-out. The publisher is the
only shape with a shadow and the only plum fill in the picture.

**Deliberately omitted.** Retry topics, the dead-letter queue, the schema
registry, and consumer group semantics. The post is about coupling, not about
delivery guarantees — and every one of those would have added an edge pointing
backwards, which is exactly the shape the post says they removed.

### The argument the shape makes

There is no edge from any subscriber back to the order service, and no edge
between subscribers. That absence *is* the thesis. A reader who takes nothing
else from the diagram should notice that the arrows only go one way.

The `annotation` shape spells it out in one quiet italic line rather than a
paragraph of caption.

### Why `editorial` and not `minimal-light`

Inside prose, a neutral corporate palette reads as a screenshot of someone else's
document. The warm paper neutrals and plum accent sit with the article's
typography instead of interrupting it. Datastores use a cool slate rather than
the pack's original rose, which read as an error state next to the red failure
family — a real bug caught by looking at the render.

### What the first draft got wrong

It included the DLQ and a retry topic, which pushed the subscriber count to five
and turned the clean three-way fan-out into a mesh. The diagram then illustrated
the opposite of the post's claim.
