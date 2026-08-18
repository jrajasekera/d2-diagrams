# Gallery

Finished diagrams, with the reasoning that produced them.

Templates show you where to *start*. These show you where to *stop*: each entry
is a diagram someone would actually publish, together with the brief it answers,
the choices behind it, and — most usefully — what was left out and why.

Each directory holds:

- `diagram.d2` — the canonical source
- `preview.svg` — a committed render (the one exception to "renders are
  disposable"; regenerate with `scripts/render_gallery.sh`)
- `design-notes.md` — brief, thesis, style pack, engine, medium, focal path,
  deliberate omissions, and the revision that mattered

| Entry | Answers | Style pack | Engine | Medium |
|---|---|---|---|---|
| [architecture-minimal](architecture-minimal/) | how a request is served | `minimal-light` | elk | README |
| [architecture-dark](architecture-dark/) | read path vs. write path | `semantic-classes` | elk | docs site with dark mode |
| [ci-cd-presentation](ci-cd-presentation/) | why deploys are safe | `presentation` | dagre | 16:9 slide |
| [event-driven-editorial](event-driven-editorial/) | what removing the mesh changed | `editorial` | elk | blog post |
| [incident-failover](incident-failover/) | how failover proceeds, in order | `minimal-light` | elk | on-call handbook |
| [sequence-authentication](sequence-authentication/) | which redirect happens when | `minimal-light` | n/a | internal docs |
| [erd-domain-focused](erd-domain-focused/) | how subscriptions relate to invoices | `minimal-light` | elk | internal docs |
| [cloud-network](cloud-network/) | that the database is not internet-reachable | `minimal-light` | elk | security review PDF |

## Start here

**[architecture-minimal](architecture-minimal/)** is the before/after pair. Its
`before.d2` is valid D2 that renders successfully and is genuinely bad: eighteen
nodes, twenty-seven equal-weight edges, eight decorative colors, and no thesis.
`diagram.d2` is the same system, designed. Comparing the two teaches more than
another page of syntax.

Open both renders side by side:

```bash
scripts/review_d2.py gallery/architecture-minimal/before.d2 \
                     gallery/architecture-minimal/diagram.d2 --png
```

## Reading the notes

The design notes are written to be argued with. They state a thesis, name what
was cut, and say what went wrong — including in diagrams that shipped. If an
omission looks wrong for your situation, it probably is: the point is that
someone decided, not that this particular set of decisions is universal.
