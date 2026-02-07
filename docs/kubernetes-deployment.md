# Kubernetes Deployment Guide

This guide covers deploying the AI-powered Todo application to Kubernetes.

## Architecture Overview

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
                    │  │ (Next.js)│   │(FastAPI) │        │
                    │  └─────────┘   └────┬─────┘        │
                    │                     │              │
                    └─────────────────────┼──────────────┘
                                          │ SSL
                                          ▼
                              ┌─────────────────────┐
                              │  Neon PostgreSQL    │
                              │  (External Cloud)   │
                              └─────────────────────┘
```

## Prerequisites

### Required Tools
- **Docker**: For building container images
- **kubectl**: Kubernetes CLI
- **Helm 3.x**: For Helm-based deployment (optional but recommended)
- **minikube/kind**: For local Kubernetes cluster (or access to cloud K8s)

### Required Accounts/Services
- **Neon**: Free PostgreSQL database ([console.neon.tech](https://console.neon.tech))
- **Groq** (optional): Free AI API for chatbot ([console.groq.com](https://console.groq.com))

## Quick Start

### 1. Set Up Local Kubernetes (minikube)

```bash
# Start minikube
minikube start --cpus=4 --memory=8192

# Enable ingress addon
minikube addons enable ingress

# Point Docker to minikube's Docker daemon
eval $(minikube docker-env)
```

### 2. Build Docker Images

```bash
# Build both backend and frontend images
./scripts/build-images.sh

# Or manually:
docker build -t todo-backend:latest -f docker/backend/Dockerfile .
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile .
```

### 3. Set Environment Variables

```bash
# Required
export DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require"
export BETTER_AUTH_SECRET="your-secret-key-minimum-32-characters-long"

# Optional (for AI chat feature)
export GROQ_API_KEY="your-groq-api-key"
```

### 4a. Deploy with Helm (Recommended)

```bash
# Deploy
./scripts/deploy-helm.sh

# Or manually:
helm upgrade --install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.groqApiKey="$GROQ_API_KEY"
```

### 4b. Deploy with kubectl (Alternative)

```bash
# Deploy
./scripts/deploy-kubectl.sh

# Or manually:
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic todo-secrets \
  --namespace todo-app \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=GROQ_API_KEY="$GROQ_API_KEY"
kubectl apply -f k8s/
```

### 5. Access the Application

```bash
# Add to /etc/hosts
echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts

# Start minikube tunnel (keep running in terminal)
minikube tunnel

# Open browser
open http://todo.local
```

## Configuration

### Helm Values

Key configuration options in `helm/todo-app/values.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicaCount` | Number of backend pods | 2 |
| `frontend.replicaCount` | Number of frontend pods | 2 |
| `ingress.enabled` | Enable ingress | true |
| `ingress.hosts[0].host` | Ingress hostname | todo.local |
| `backend.resources.limits.memory` | Backend memory limit | 512Mi |
| `frontend.resources.limits.memory` | Frontend memory limit | 512Mi |

### Secrets

Required secrets (provide via `--set` or environment):

| Secret | Description |
|--------|-------------|
| `secrets.databaseUrl` | Neon PostgreSQL connection string |
| `secrets.betterAuthSecret` | JWT signing secret (min 32 chars) |
| `secrets.groqApiKey` | Groq API key (optional) |
| `secrets.openaiApiKey` | OpenAI API key (optional) |

## Production Deployment

### Using Production Values

```bash
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-production.yaml \
  --namespace todo-app-prod \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.groqApiKey="$GROQ_API_KEY"
```

### TLS/HTTPS

1. Install cert-manager:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

2. Create ClusterIssuer for Let's Encrypt:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

3. Enable TLS in values:
```yaml
ingress:
  tls:
    - secretName: todo-tls
      hosts:
        - todo.yourdomain.com
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

### Scaling

The application includes Horizontal Pod Autoscaler (HPA) configurations:

```bash
# View HPA status
kubectl get hpa -n todo-app

# Manual scaling
kubectl scale deployment/todo-backend --replicas=5 -n todo-app
```

## Troubleshooting

### Check Pod Status

```bash
# List pods
kubectl get pods -n todo-app

# Check pod logs
kubectl logs -f deployment/todo-backend -n todo-app
kubectl logs -f deployment/todo-frontend -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app
```

### Common Issues

#### Pods stuck in Pending
```bash
# Check node resources
kubectl describe nodes

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

#### Database Connection Failed
```bash
# Verify secret
kubectl get secret todo-secrets -n todo-app -o yaml

# Test from within cluster
kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -- \
  psql "$DATABASE_URL" -c "SELECT 1"
```

#### Ingress Not Working
```bash
# Check ingress status
kubectl describe ingress -n todo-app

# Verify ingress controller
kubectl get pods -n ingress-nginx
```

### Reset Deployment

```bash
# Uninstall Helm release
helm uninstall todo-app -n todo-app

# Or delete kubectl resources
kubectl delete -f k8s/

# Delete namespace
kubectl delete namespace todo-app
```

## Directory Structure

```
/
├── docker/
│   ├── backend/Dockerfile    # Production backend image
│   └── frontend/Dockerfile   # Production frontend image
├── helm/
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-production.yaml
│       └── templates/
├── k8s/
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── ingress.yaml
└── scripts/
    ├── build-images.sh
    ├── deploy-helm.sh
    └── deploy-kubectl.sh
```

## Related Documentation

- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [Architecture Overview](../specs/architecture.md)
- [API Documentation](../specs/api/README.md)
