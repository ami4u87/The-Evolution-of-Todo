# Phase IV: Local Kubernetes Deployment Plan

## Overview
Deploy the AI-powered Todo application (FastAPI backend + Next.js frontend + Neon PostgreSQL) to Kubernetes with Helm charts and production-ready configurations.

## Tech Stack

### Container Runtime
- **Docker**: Multi-stage builds for optimized images
- **Container Registry**: Local (minikube) or Docker Hub

### Orchestration
- **Kubernetes**: Container orchestration
- **Helm**: Package manager for Kubernetes
- **Ingress NGINX**: Traffic routing

### Infrastructure
- **Database**: Neon Serverless PostgreSQL (external)
- **Secrets Management**: Kubernetes Secrets + sealed-secrets (optional)

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Kubernetes Cluster          │
                    │                                     │
┌───────────┐       │  ┌─────────────────────────────┐   │
│  Browser  │───────┼──│     Ingress Controller      │   │
└───────────┘       │  └──────────┬──────────────────┘   │
                    │             │                       │
                    │    ┌────────┴────────┐             │
                    │    │                 │             │
                    │    ▼                 ▼             │
                    │  ┌─────────┐   ┌──────────┐        │
                    │  │Frontend │   │ Backend  │        │
                    │  │ Service │   │ Service  │        │
                    │  └────┬────┘   └────┬─────┘        │
                    │       │             │              │
                    │       ▼             ▼              │
                    │  ┌─────────┐   ┌──────────┐        │
                    │  │Frontend │   │ Backend  │        │
                    │  │  Pods   │   │  Pods    │        │
                    │  │(Next.js)│   │(FastAPI) │        │
                    │  └─────────┘   └────┬─────┘        │
                    │                     │              │
                    └─────────────────────┼──────────────┘
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │  Neon PostgreSQL    │
                              │  (External Cloud)   │
                              └─────────────────────┘
```

## Directory Structure

```
/
├── docker/
│   ├── backend/
│   │   └── Dockerfile          # Production Dockerfile for FastAPI
│   └── frontend/
│       └── Dockerfile          # Production Dockerfile for Next.js
│
├── helm/
│   └── todo-app/
│       ├── Chart.yaml          # Helm chart metadata
│       ├── values.yaml         # Default configuration values
│       ├── values-production.yaml
│       └── templates/
│           ├── _helpers.tpl    # Template helpers
│           ├── namespace.yaml  # Namespace definition
│           ├── secrets.yaml    # Kubernetes secrets
│           ├── configmap.yaml  # ConfigMap for non-sensitive config
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── ingress.yaml    # Ingress rules
│           └── hpa.yaml        # Horizontal Pod Autoscaler
│
├── k8s/
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── ingress.yaml
│
└── scripts/
    ├── build-images.sh         # Build Docker images
    ├── deploy-helm.sh          # Deploy with Helm
    └── deploy-kubectl.sh       # Deploy with kubectl
```

## Environment Variables

### Backend (FastAPI)
| Variable | Description | Source |
|----------|-------------|--------|
| DATABASE_URL | Neon PostgreSQL connection string | Secret |
| BETTER_AUTH_SECRET | JWT signing secret | Secret |
| JWT_ALGORITHM | JWT algorithm (HS256) | ConfigMap |
| API_PREFIX | API route prefix | ConfigMap |
| DEBUG | Debug mode flag | ConfigMap |
| CORS_ORIGINS | Allowed CORS origins | ConfigMap |
| AI_PROVIDER | AI provider (groq/openai) | ConfigMap |
| GROQ_API_KEY | Groq API key | Secret |
| OPENAI_API_KEY | OpenAI API key | Secret |

### Frontend (Next.js)
| Variable | Description | Source |
|----------|-------------|--------|
| NEXT_PUBLIC_API_URL | Backend API URL | ConfigMap |
| BETTER_AUTH_SECRET | JWT signing secret | Secret |
| BETTER_AUTH_URL | Auth callback URL | ConfigMap |

## Helm Values Schema

```yaml
# values.yaml
global:
  namespace: todo-app

backend:
  replicaCount: 2
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi
  env:
    debug: "false"
    apiPrefix: "/api"
    jwtAlgorithm: "HS256"
    aiProvider: "groq"

frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

secrets:
  # These should be provided via --set or values file
  databaseUrl: ""
  betterAuthSecret: ""
  groqApiKey: ""
  openaiApiKey: ""
```

## Deployment Steps

### Prerequisites
1. Kubernetes cluster (minikube, kind, or cloud provider)
2. kubectl configured
3. Helm 3.x installed
4. Docker installed

### Quick Start (Helm)
```bash
# Build images
./scripts/build-images.sh

# Create namespace
kubectl create namespace todo-app

# Deploy with Helm
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.betterAuthSecret="your-secret" \
  --set secrets.groqApiKey="your-groq-key"

# Verify deployment
kubectl get pods -n todo-app
```

### Quick Start (kubectl)
```bash
# Build images
./scripts/build-images.sh

# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml  # Edit with your values first
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml
```

## Security Considerations

1. **Secrets Management**
   - Use Kubernetes Secrets for sensitive data
   - Consider sealed-secrets or external-secrets for GitOps
   - Never commit plain secrets to git

2. **Network Policies**
   - Restrict pod-to-pod communication
   - Allow only necessary ingress/egress

3. **Pod Security**
   - Run as non-root user
   - Read-only root filesystem where possible
   - Resource limits enforced

4. **TLS**
   - Use cert-manager for automatic TLS
   - HTTPS everywhere in production

## Monitoring & Observability

1. **Health Checks**
   - Liveness probes for container health
   - Readiness probes for traffic routing

2. **Logging**
   - Structured JSON logs
   - Forward to centralized logging (ELK, Loki)

3. **Metrics**
   - Prometheus metrics endpoint
   - Grafana dashboards

## Scaling Strategy

1. **Horizontal Pod Autoscaler (HPA)**
   - Scale based on CPU/memory utilization
   - Min 2, Max 10 replicas

2. **Resource Quotas**
   - Namespace-level resource limits
   - Prevent resource exhaustion
