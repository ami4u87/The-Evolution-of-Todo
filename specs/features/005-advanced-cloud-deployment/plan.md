# Phase V: Advanced Cloud Deployment Plan

## Overview
Extend the Todo application with Event-Driven Architecture using Kafka and Dapr,
deployed to DigitalOcean Kubernetes Service (DOKS).

## Architecture

```
                         ┌──────────────────────────────────────────────────┐
                         │           DigitalOcean Kubernetes (DOKS)        │
                         │                                                 │
  ┌──────────┐           │  ┌──────────────────┐                          │
  │ Browser  │───HTTPS───┼──│  DO Load Balancer │                          │
  └──────────┘           │  │  + Ingress NGINX  │                          │
                         │  └────────┬─────────┘                          │
                         │           │                                     │
                         │    ┌──────┴──────┐                             │
                         │    ▼             ▼                              │
                         │ ┌──────────┐ ┌──────────────────────────┐      │
                         │ │ Frontend │ │ Backend Pod               │      │
                         │ │ (Next.js)│ │ ┌──────────┐ ┌─────────┐│      │
                         │ └──────────┘ │ │ FastAPI  │ │  Dapr   ││      │
                         │              │ │ app.main │ │ Sidecar ││      │
                         │              │ └────┬─────┘ └────┬────┘│      │
                         │              └──────┼────────────┼─────┘      │
                         │                     │            │             │
                         │                     │     ┌──────┴──────┐     │
                         │                     │     │ Kafka (Strimzi)│   │
                         │                     │     │  task-events   │   │
                         │                     │     └───────────────┘   │
                         └─────────────────────┼─────────────────────────┘
                                               │ SSL
                                               ▼
                                   ┌─────────────────────┐
                                   │  Neon PostgreSQL    │
                                   └─────────────────────┘
```

## Tech Stack Additions (Phase V)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Message Broker | Apache Kafka (Strimzi) | Event streaming |
| App Runtime | Dapr | Pub/sub, sidecar pattern |
| Cloud Provider | DigitalOcean DOKS | Managed Kubernetes |
| TLS | cert-manager + Let's Encrypt | Automatic HTTPS |
| Load Balancer | DO Load Balancer | Ingress traffic |

## Event-Driven Architecture

### Event Types
| Event | Topic | Trigger |
|-------|-------|---------|
| `task.created` | `task-events` | POST /api/tasks |
| `task.updated` | `task-events` | PUT /api/tasks/{id} |
| `task.completed` | `task-events` | PATCH /api/tasks/{id}/complete |
| `task.deleted` | `task-events` | DELETE /api/tasks/{id} |

### Event Schema
```json
{
  "id": "uuid",
  "type": "task.created",
  "source": "todo-backend",
  "time": "2026-02-01T00:00:00Z",
  "data": {
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "status": "string"
  }
}
```

### Dapr Integration
- Dapr sidecar injected into backend pods
- Pub/sub component bound to Kafka
- Backend publishes events via Dapr HTTP API
- Future consumers subscribe via Dapr pub/sub

## Directory Structure (New/Modified)

```
/
├── backend/
│   └── app/
│       ├── events/                 # NEW: Event-driven infrastructure
│       │   ├── __init__.py
│       │   ├── models.py          # Event schema definitions
│       │   ├── publisher.py       # Dapr/Kafka event publisher
│       │   └── topics.py         # Topic constants
│       ├── services/
│       │   └── task_service.py    # MODIFIED: emit events
│       ├── config.py              # MODIFIED: event config
│       └── main.py                # MODIFIED: event health check
│
├── helm/
│   └── todo-app/
│       ├── values-doks.yaml        # NEW: DOKS-specific values
│       └── templates/
│           ├── dapr-pubsub.yaml    # NEW: Dapr pub/sub component
│           └── dapr-subscription.yaml # NEW: Dapr subscriptions
│
├── k8s/
│   ├── kafka/                      # NEW: Strimzi Kafka manifests
│   │   ├── strimzi-operator.yaml
│   │   ├── kafka-cluster.yaml
│   │   └── kafka-topic.yaml
│   └── dapr/                       # NEW: Dapr components
│       ├── dapr-pubsub-kafka.yaml
│       └── dapr-subscription.yaml
│
├── scripts/
│   ├── deploy-doks.sh              # NEW: DOKS deployment script
│   └── setup-doks-prereqs.sh       # NEW: Install Strimzi + Dapr
│
└── docs/
    └── doks-deployment.md          # NEW: DOKS deployment guide
```

## Secrets (DOKS)

| Secret | Source | Description |
|--------|--------|-------------|
| DATABASE_URL | K8s Secret | Neon PostgreSQL connection |
| BETTER_AUTH_SECRET | K8s Secret | JWT signing key |
| GROQ_API_KEY | K8s Secret | AI chat API key |
| DO_TOKEN | env var | DigitalOcean API token (deploy only) |
