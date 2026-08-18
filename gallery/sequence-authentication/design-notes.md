# sequence-authentication — one flow, no branches

**Brief.** "Explain our OIDC login to a new backend engineer. They keep asking
which redirect happens when."

**Thesis.** The browser makes three hops, and the application never sees the
user's password.

**Style pack / engine / medium.** `minimal-light` · none — sequence diagrams
ignore the layout engine · internal docs.

**Focal path.** Top to bottom. In a sequence diagram the order *is* the message,
so there is no separate emphasis to add.

**Deliberately omitted.** Token refresh, logout, the consent screen, and every
error branch. Those are three more sequence diagrams, not three more branches on
this one — a sequence diagram with conditionals stops being readable at about
two.

### What the style pack still does here

Sequence diagrams do their own layout, but participants are ordinary shapes, so
the semantic classes still apply: the Application is the accent, the IdP is a
dashed `external_system`, and the lifelines inherit each participant's stroke
color. That is enough to keep this diagram in the same visual family as the
architecture boards without fighting the sequence renderer.

Participant order is declaration order, and message order is declaration order.
There is no layout engine to blame if the crossings are bad — reorder the
declarations.

### Why the password claim is visible

`user → idp: credentials + MFA` is drawn from the user directly to the identity
provider, crossing over the application's lifeline without touching it. Someone
who reads only the arrows still gets the security property.

### Labels are the deliverable

The lazy version of this diagram labels the hops `redirect`, `redirect`,
`redirect`, and answers nothing — the engineer asked *which redirect happens
when*. `302 to IdP (+ state, PKCE challenge)`, `302 back with code`, and
`POST /token (code + verifier)` are the answer. In a sequence diagram the shapes
are nearly free; the edge labels are the whole deliverable.
