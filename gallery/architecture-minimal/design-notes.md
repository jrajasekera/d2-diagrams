# architecture-minimal — before and after

The only entry in this gallery with a `before.d2`. Both files compile. Both pass
`scripts/check_d2.sh`. That is the lesson.

Counting leaf nodes (containers listed separately) and declared connections:

| | `before.d2` | `diagram.d2` |
|---|---|---|
| Leaf nodes | 18 | 9 |
| Edges | 26 | 9 |
| Containers | 0 | 3 |
| Distinct fill colors | 8 | 4 families |
| Edge weights | 1 | 3 |

**Brief.** "Show how a customer request is served, for the README of the platform
repo. New engineers should understand the request path on day one."

**Thesis.** A customer request is served synchronously by the API from Postgres
and Redis; everything asynchronous hangs off one queue.

**Style pack / engine / medium.** `minimal-light` · elk · web documentation.

**Focal path.** `customer → edge.waf → app.api → data.db`, carried by
`primary_edge` — indigo, stroke-width 3. It is the only heavy line in the
diagram, so the eye finds it before reading a single label.

**Deliberately omitted.** Observability (Prometheus, Loki, Grafana), the auth,
search, and notification services, the read replica, and S3. None of them are on
the request path a new engineer needs on day one; each belongs on its own board.
Also gone: version numbers and instance types.

### What is wrong with `before.d2`

1. **No thesis.** It is an inventory, not an argument. Nothing tells you what to
   look at, so you read all 18 boxes in arbitrary order.
2. **Eight decorative colors with no meaning.** Red on `Customer`, green on the
   CDN, magenta on Postgres. A reader scanning for problems finds a red box that
   means nothing. Worse, the semantics are now spent: there is no color left to
   say "this is the broken one".
3. **Every edge weighs the same.** Twenty-seven identical arrows means the
   request path and the Grafana scrape look equally important.
4. **Two abstraction levels at once.** "Go 1.22, 6 pods" and "db.r6g.xlarge" are
   deployment facts sitting next to a component-level box called "Auth Service".
5. **No containers**, so nothing indicates a trust boundary or a tier.
6. **Observability inverted the graph.** `metrics → api`, `logs → worker`, and
   `grafana → metrics` add seven edges pointing *backwards* against the reading
   direction, which is most of why the layout became a hairball.

### The revision that mattered

The temptation when cutting `before.d2` down is to keep the read replica and the
auth service "because they are real". They are — and they drag in three more
edges, one of which has to cross the Data container, which elk then routes around
the outside of everything.

Cutting nodes removes routing problems that no amount of styling would have
fixed. **Structural fixes beat cosmetic ones**, and they are almost always
available earlier than they feel available.
