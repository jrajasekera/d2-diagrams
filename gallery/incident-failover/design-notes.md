# incident-failover — a runbook told in steps

**Brief.** "Runbook diagram for the primary-database failover, for the on-call
handbook. It should be obvious what breaks and what takes over."

**Thesis.** When the primary loses its heartbeat, the monitor promotes the
replica and the API repoints — two actions, in that order.

**Style pack / engine / medium.** `minimal-light` · elk · internal docs, also
printed into the on-call handbook.

**Focal path.** Changes per step, which is the whole design: `monitor → primary`
during detection, `api → replica` after promotion.

**Deliberately omitted.** Connection-pool draining, DNS TTLs, the read-replica
lag check, and the "is it actually down or is it the network" decision. Each is a
real runbook step and none of them is a *picture*.

### Why steps and not one board

A single board showing both the failed primary and the promoted replica is how
people promote a replica that was never demoted. Order is the safety property, so
order has to be in the diagram's structure, not in a caption.

`steps` inherit cumulatively, so each board shows everything that has happened so
far — which matches how someone reads a runbook mid-incident. Render the
walkthrough as one animated SVG:

```bash
d2 --animate-interval=2000 diagram.d2 failover.svg
```

The committed `preview.svg` is that animation.

### Color discipline

Red appears exactly once, on the primary, and only from the `detect` step onward.
Before detection the primary is an ordinary datastore. If red had also been used
for "replica" or "monitor", the one moment that matters would be invisible.

The demoted primary drops to `opacity: 0.3` in the final step rather than
disappearing. Deleting it would leave the reader unsure whether it was stopped or
just undrawn — and "is the old primary definitely not taking writes" is the
question the runbook exists to answer.

### Why not `scenarios`

`scenarios` inherit from the base board but not from each other, so each one
resets. Used here, the failover would read as three unrelated situations rather
than one incident progressing — which is precisely the misreading the diagram
exists to prevent. Reach for `scenarios` when the boards are alternatives
(normal vs. degraded), and for `steps` when they are a sequence.
