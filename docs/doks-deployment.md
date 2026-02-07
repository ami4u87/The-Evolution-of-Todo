# DigitalOcean Kubernetes (DOKS) Deployment Guide

Deploy the AI-powered Todo application with event-driven architecture to DigitalOcean Kubernetes.

## Architecture

```
Internet → DO Load Balancer → NGINX Ingress
                                    ├── /api  → Backend (FastAPI + Dapr sidecar)
                                    └── /     → Frontend (Next.js)
                                                     │
                                    Backend ←→ Dapr ←→ Kafka (Strimzi)
                                        │
                                        └── Neon PostgreSQL (external)
```

## Prerequisites

### Required Tools
- **doctl**: DigitalOcean CLI ([install](https://docs.digitalocean.com/reference/doctl/how-to/install/))
- **kubectl**: Kubernetes CLI
- **helm**: Helm 3.x
- **docker**: Container runtime

### Required Accounts
- **DigitalOcean**: Account with DOKS cluster
- **Neon**: PostgreSQL database
- **Groq** (optional): AI chat API key

## Setup

### 1. Create DOKS Cluster

```bash
# Login to DigitalOcean
doctl auth init

# Create Kubernetes cluster
doctl kubernetes cluster create todo-cluster \
  --region sgp1 \
  --node-pool "name=default;size=s-2vcpu-4gb;count=3" \
  --version latest

# Save kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster
```

### 2. Create Container Registry

```bash
# Create registry
doctl registry create todo-app

# Connect registry to cluster
doctl registry kubernetes-manifest | kubectl apply -f -
```

### 3. Install Infrastructure Components

```bash
# Install Strimzi, Dapr, NGINX Ingress, cert-manager
./scripts/setup-doks-prereqs.sh
```

This installs:
- **NGINX Ingress Controller** - Traffic routing with DO Load Balancer
- **cert-manager** - Automatic TLS certificates
- **Strimzi Kafka Operator** - Kafka cluster management
- **Dapr** - Distributed application runtime

### 4. Deploy the Application

```bash
# Set secrets
export DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require"
export BETTER_AUTH_SECRET="your-secret-minimum-32-characters"
export GROQ_API_KEY="your-groq-api-key"
export DO_REGISTRY="todo-app"

# Build, push, and deploy
./scripts/deploy-doks.sh
```

### 5. Configure DNS

After deployment, get the Load Balancer IP:

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

Add a DNS A record pointing your domain to this IP.

## Event-Driven Architecture

### How Events Work

1. User performs a task operation (create/update/delete/complete)
2. FastAPI backend processes the request and commits to Neon PostgreSQL
3. Backend publishes a CloudEvents-format event via Dapr sidecar
4. Dapr routes the event to Kafka topic `task-events`
5. Future consumers can subscribe to these events

### Event Types

| Event | Trigger | Topic |
|-------|---------|-------|
| `task.created` | POST /api/tasks | task-events |
| `task.updated` | PUT /api/tasks/{id} | task-events |
| `task.completed` | PATCH /api/tasks/{id}/complete | task-events |
| `task.deleted` | DELETE /api/tasks/{id} | task-events |

### Event Schema (CloudEvents)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "task.created",
  "source": "todo-backend",
  "specversion": "1.0",
  "time": "2026-02-01T00:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "Buy groceries",
    "status": "pending"
  }
}
```

### Monitoring Events

```bash
# View event logs from backend
kubectl logs -f deployment/todo-app-backend -n todo-app | grep "Event:"

# Check Kafka topics
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Consume events from topic
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh --topic task-events \
  --bootstrap-server localhost:9092 --from-beginning
```

## Scaling

### Horizontal Pod Autoscaler

Both backend and frontend have HPA configured:

```bash
# View autoscaler status
kubectl get hpa -n todo-app

# Manual scaling
kubectl scale deployment/todo-app-backend --replicas=5 -n todo-app
```

### Kafka Scaling

To scale Kafka for production:

```bash
# Edit kafka-cluster.yaml and set replicas: 3
kubectl apply -f k8s/kafka/kafka-cluster.yaml
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
kubectl logs -f <pod-name> -n todo-app
```

### Check Dapr Sidecar
```bash
# Verify Dapr is injected
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.name}{","}{end}{"\n"}{end}'

# Check Dapr dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080
```

### Check Kafka
```bash
# Verify Kafka cluster
kubectl get kafka -n kafka
kubectl get kafkatopic -n kafka

# Check Kafka logs
kubectl logs -f todo-kafka-kafka-0 -n kafka
```

### Common Issues

**Events not publishing**: Check Dapr sidecar is running alongside backend pod. Verify `dapr.enabled=true` in values.

**Kafka not ready**: Strimzi takes 2-5 minutes to provision. Run:
```bash
kubectl wait kafka/todo-kafka --for=condition=Ready -n kafka --timeout=300s
```

**Image pull errors**: Ensure DO registry is connected:
```bash
doctl registry kubernetes-manifest | kubectl apply -f -
```

## Cost Estimate (DigitalOcean)

| Resource | Spec | Monthly Cost |
|----------|------|-------------|
| DOKS Cluster | 3x s-2vcpu-4gb | ~$36 |
| Load Balancer | 1x | ~$12 |
| Container Registry | Basic | ~$5 |
| **Total** | | **~$53/mo** |

*Neon PostgreSQL free tier included. Groq AI free tier included.*

## Cleanup

```bash
# Remove application
helm uninstall todo-app -n todo-app

# Remove infrastructure
helm uninstall strimzi-kafka-operator -n kafka
helm uninstall dapr -n dapr-system
helm uninstall ingress-nginx -n ingress-nginx
helm uninstall cert-manager -n cert-manager

# Delete cluster
doctl kubernetes cluster delete todo-cluster

# Delete registry
doctl registry delete todo-app
```
