# erd-domain-focused — five tables out of sixty

**Brief.** "New engineer asked how subscriptions and invoices relate. Do not send
them the 60-table schema dump."

**Thesis.** A subscription generates invoices on a cycle; payments settle
invoices, not subscriptions.

**Style pack / engine / medium.** `minimal-light` · elk · internal docs.

**Focal path.** `subscription → invoice → payment`, left to right.

**Deliberately omitted.** Fifty-five tables, and within the five that remain,
every audit column, index, soft-delete flag, and nullable settings field.

### The omission is the answer

An ERD generated from the schema answers no question in particular. This one
answers exactly the question that was asked, and the reason it can is that
someone chose what to leave out.

The columns that survive are the ones carrying the relationship — the keys, the
status, and the two amounts that let a reader check the arithmetic. `plans.code`
and `customers.email` stay because they are how a human identifies a row when
debugging.

The one thing the diagram makes unmissable is that `payments.invoice_id` points
at `invoices`, not at `subscriptions`. That is the fact the new engineer was
missing, and it is legible from the arrow alone.

### Why elk

Foreign-key edges in D2 attach to a *specific row* inside a `sql_table` shape,
not to the shape's border. Dagre routes these with curves that loop back across
the table body and pass under other rows; elk keeps them orthogonal and clear of
the tables. This is the one diagram type where the engine choice is close to
mandatory.

### The pull to resist

`subscription_items` belongs in this schema and feels wrong to omit. Including it
adds a fourth hop to the focal path and makes the answer to "how do subscriptions
and invoices relate" one step longer than the question deserved. Completeness is
not a goal an ERD can usefully pursue; answering the question is.
