# cloud-network — a diagram that has to prove something

**Brief.** "Security review wants one picture showing that the database is not
reachable from the internet."

**Thesis.** The only path from the internet ends at the load balancer in the
public subnet; the data subnet has no inbound route from outside the VPC.

**Style pack / engine / medium.** `minimal-light` · elk · review document,
exported to PDF.

**Focal path.** `internet → alb → app → db`, with every boundary crossing
visible.

**Deliberately omitted.** Security-group rules, NACLs, IAM policies, and the
bastion path. Each is a separate question, and putting them here would bury the
single claim being made.

### The containers are the argument

Every container is a real trust boundary. A flattened version of this diagram
would be prettier, more compact, and would prove nothing — the nesting is the
evidence. This is one of the few cases where "more boxes" is the right answer.

The data subnet's label carries the claim in words as well as structure
("no inbound route from the internet"), because a reviewer should not have to
infer a security property from the absence of an arrow.

### Print-specific choices

It is exported to PDF, so:

- there is a **legend** — no tooltips exist on paper
- no stroke is thinner than 1px at the intended print scale
- the semantics survive grayscale: public-facing components are heavier-stroked
  and filled, not merely a different hue

### What the first draft got wrong

It included a `nat → internet` egress edge. True, and harmless-sounding, but elk
routed it around the entire VPC, producing a long line that crossed all three
subnet boundaries — visually implying exactly the kind of unrestricted path the
diagram exists to disprove. The NAT Gateway's name already says what it does.

It also made the diagram wider, for something the NAT Gateway's own name already
says. **Low-value edges cost more than they look** — and the cost is rarely just
the line itself, it is what the router does to accommodate it.
