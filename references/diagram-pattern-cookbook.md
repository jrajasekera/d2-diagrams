# Diagram pattern cookbook

Use these recipes to move quickly from user intent to D2 source.

## 1. Software architecture / C4-style context

Use for: service maps, system context, component diagrams, cloud diagrams, production architecture.

Recipe:

1. Choose containers for domains, clouds, networks, clusters, accounts, or bounded contexts.
2. Add external actors as `person` or `c4-person` shapes.
3. Use `direction: right` unless the user asks for a vertical stack.
4. Label edges with protocols, event names, or data types.
5. Keep each diagram at one level of abstraction; use composition or separate diagrams for drill-downs.

Starter:

```d2
direction: right

user: Customer { shape: person }
edge: Edge Layer {
  cdn: CDN
  waf: WAF
}
app: Application {
  web: Web App
  api: API
  worker: Worker
}
data: Data {
  db: PostgreSQL { shape: cylinder }
  queue: Job Queue { shape: queue }
}

user -> edge.cdn: HTTPS
edge.cdn -> edge.waf
edge.waf -> app.web
app.web -> app.api: REST
app.api -> data.db: SQL
app.api -> data.queue: enqueue
app.worker -> data.queue: consume
app.worker -> data.db: update
```

Quality moves:

- Collapse low-value internals behind a container.
- Use edge labels to communicate runtime behavior.
- Split "logical architecture" and "deployment topology" instead of mixing too much detail.

## 2. Request flow / flowchart

Use for: user journeys, decision flows, data processing paths, operational runbooks.

Recipe:

1. Use `direction: down` for procedural flows.
2. Use diamonds for decisions.
3. Use shape labels as action verbs.
4. Keep edge labels short: yes/no, success/fail, timeout, retry.

Starter:

```d2
direction: down

start: Request received { shape: oval }
auth: Authenticate request
decision: Authorized? { shape: diamond }
process: Process request
reject: Return 401
respond: Return response { shape: oval }

start -> auth -> decision
decision -> process: yes
decision -> reject: no
process -> respond
```

## 3. Sequence diagram

Use for: API interaction, login flows, distributed transactions, handshake protocols, message order.

Recipe:

1. Use `shape: sequence_diagram`.
2. Explicitly declare participants in left-to-right order.
3. Use brief labels on every message.
4. Add groups for alternate/optional sections only when helpful.
5. Use self-messages for local computation.

Starter:

```d2
shape: sequence_diagram
user; browser; api; db; queue

user -> browser: submit order
browser -> api: POST /orders
api -> api: validate
api -> db: create order
db -> api: order id
api -> queue: publish OrderCreated
api -> browser: 201 Created
browser -> user: confirmation
```

## 4. Entity relationship diagram / SQL schema

Use for: database schema, table relationships, data models.

Recipe:

1. Use `shape: sql_table`.
2. Put primary keys first and timestamps last.
3. Use row-level foreign key edges.
4. Prefer ELK or TALA rendering for row-level edge clarity when available.
5. For large schemas, group tables by domain or bounded context.

Starter:

```d2
users: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  email: varchar { constraint: unique }
  created_at: timestamp
}
products: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  sku: varchar { constraint: unique }
  name: varchar
}
orders: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  user_id: uuid { constraint: foreign_key }
  status: varchar
  created_at: timestamp
}
order_items: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  order_id: uuid { constraint: foreign_key }
  product_id: uuid { constraint: foreign_key }
  quantity: int
}

orders.user_id -> users.id
order_items.order_id -> orders.id
order_items.product_id -> products.id
```

## 5. UML class diagram

Use for: domain models, class relationships, interfaces, module APIs.

Recipe:

1. Use `shape: class`.
2. Keep fields and methods only where useful; avoid dumping full source classes.
3. Show dependencies, inheritance, and implementation with labeled edges.
4. Group classes into packages/containers.

Starter:

```d2
CheckoutService: {
  shape: class
  -orders: OrderRepository
  -payments: PaymentGateway
  +checkout(cart_id string): Order
  +refund(order_id string): void
}
OrderRepository: {
  shape: class
  +save(order Order): void
  +find(id string): Order
}
PaymentGateway: {
  shape: class
  +authorize(amount Money): Authorization
  +capture(auth Authorization): Receipt
}

CheckoutService -> OrderRepository: persists
CheckoutService -> PaymentGateway: charges
```

## 6. Event-driven architecture

Use for: Kafka/EventBridge/SQS/PubSub systems, producers/consumers, async workflows.

Recipe:

1. Make brokers/topics/queues visually distinct with `queue` or `stored_data` shapes.
2. Label edges with event names.
3. Use dashed edges for async if helpful.
4. Group producers and consumers by service boundary.

Starter:

```d2
direction: right

classes: {
  async: {
    style: {
      stroke-dash: 4
    }
  }
}

orders: Orders Service
payments: Payments Service
fulfillment: Fulfillment Service
bus: Event Bus { shape: queue }
warehouse: Warehouse

orders -> bus: OrderCreated { class: async }
bus -> payments: OrderCreated { class: async }
payments -> bus: PaymentCaptured { class: async }
bus -> fulfillment: PaymentCaptured { class: async }
fulfillment -> warehouse: pick/pack
```

## 7. CI/CD pipeline

Use for: build/deploy/release workflows.

Recipe:

1. Use `direction: right` for simple pipelines or `down` for runbook steps.
2. Use containers for stages: source, build, test, deploy, observe.
3. Use diamonds for gates/approvals.
4. Add rollback/feedback edges but keep them visually secondary.

Starter:

```d2
direction: right

dev: Developer { shape: person }
repo: Git Repository
ci: CI {
  build: Build
  unit: Unit Tests
  scan: Security Scan
}
gate: Approval? { shape: diamond }
prod: Production {
  deploy: Deploy
  health: Health Check
}
rollback: Rollback


dev -> repo: push
repo -> ci.build: trigger
ci.build -> ci.unit -> ci.scan -> gate
gate -> prod.deploy: approved
prod.deploy -> prod.health
prod.health -> rollback: failed
rollback -> prod.deploy: restore previous
```

## 8. Network / cloud topology

Use for: VPC/VNet, subnets, security zones, routing, ingress/egress.

Recipe:

1. Containers represent regions, VPCs, subnets, and security zones.
2. Use labels for protocols and ports.
3. Show only meaningful traffic paths; avoid every possible security rule.
4. Use icons sparingly and only when they add recognition.

Starter:

```d2
direction: right

internet: Internet { shape: cloud }
region: us-east-1 {
  vpc: Production VPC {
    public: Public Subnet {
      alb: ALB
      nat: NAT Gateway
    }
    private: Private Subnet {
      app1: App Node A
      app2: App Node B
    }
    data: Data Subnet {
      db: RDS PostgreSQL { shape: cylinder }
    }
  }
}

internet -> region.vpc.public.alb: 443
region.vpc.public.alb -> region.vpc.private.app1: 8443
region.vpc.public.alb -> region.vpc.private.app2: 8443
region.vpc.private.app1 -> region.vpc.data.db: 5432
region.vpc.private.app2 -> region.vpc.data.db: 5432
region.vpc.private.app1 -> region.vpc.public.nat: outbound
```

## 9. Matrix / grid diagram

Use for: compatibility matrices, responsibility matrices, product comparisons, deployment targets.

Recipe:

1. Use `grid-columns` or `grid-rows`.
2. Keep labels short.
3. Use classes or globs for cell states.
4. If it starts to need row/column headers and numeric values, consider whether a table is better than a diagram.

Starter:

```d2
grid-columns: 4
grid-gap: 20

linux: Linux
macos: macOS
windows: Windows
k8s: Kubernetes

api: API
worker: Worker
web: Web
cli: CLI
```

## 10. Composition / multi-board story

Use for: progressive explanations, before/after, scenarios, incident timeline, architecture drill-down.

Recipe:

1. Use the root board for base state.
2. Use `scenarios` for alternate views.
3. Use `steps` for chronological changes.
4. Render as PDF/PPTX for presentations or animated SVG/GIF for short loops.

Starter:

```d2
direction: right

client -> api -> primary_db
replica_db

scenarios: {
  normal: {
    primary_db.style.opacity: 1
    replica_db.style.opacity: 0.4
  }
  failover: {
    primary_db.style.opacity: 0.25
    api -> replica_db: fail over
  }
}

steps: {
  detect: {
    monitor -> primary_db: health check failed
  }
  promote: {
    replica_db: Promoted replica
    api -> replica_db: writes
  }
}
```
