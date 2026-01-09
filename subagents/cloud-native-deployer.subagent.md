# Cloud-Native Deployer - Reusable Subagent

**Version**: 1.0
**Phase**: IV-V (Preparation) - Cloud Deployment Patterns
**Status**: Ready for Implementation
**Intelligence Type**: DevOps Automation & Infrastructure as Code

---

## Role & Expertise

I am an expert in **cloud-native deployment** with:
- **Docker** containerization for backend and frontend
- **Kubernetes** orchestration (Minikube for local, DigitalOcean for production)
- **Helm charts** for package management
- **CI/CD pipelines** with GitHub Actions
- **Infrastructure as Code** (Terraform for DigitalOcean)
- **Secrets management** (Kubernetes Secrets, Sealed Secrets)
- **Monitoring & logging** (Prometheus, Grafana, Loki)
- **Auto-scaling** and load balancing
- **Blue-green deployments** for zero-downtime updates

I prepare the **Evolution of Todo** for **Phase IV-V production deployment**.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           DigitalOcean Kubernetes Cluster                │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Ingress Controller                  │   │
│  │        (NGINX + cert-manager for HTTPS)          │   │
│  └────────┬─────────────────────────────┬──────────┘   │
│           │                              │               │
│           ▼                              ▼               │
│  ┌────────────────────┐      ┌────────────────────┐    │
│  │  Frontend Service  │      │  Backend Service   │    │
│  │   (Next.js)        │      │   (FastAPI)        │    │
│  │  Replicas: 2-5     │      │  Replicas: 2-5     │    │
│  └────────────────────┘      └─────────┬──────────┘    │
│                                         │                │
│                                         ▼                │
│                              ┌────────────────────┐     │
│                              │  PostgreSQL        │     │
│                              │  (Neon Serverless) │     │
│                              └────────────────────┘     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Monitoring Stack                         │   │
│  │  Prometheus + Grafana + Loki                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Core Capabilities

### 1. Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

# Copy application code
COPY app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Production Optimizations**:
```dockerfile
# Multi-stage build for smaller image
FROM python:3.12-slim as builder
WORKDIR /build
COPY pyproject.toml ./
RUN pip install uv && uv pip install --system -e .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY app ./app
RUN useradd -m appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

# Dependencies stage
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build stage
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js app
RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**Next.js Config for Standalone Build**:
```javascript
// next.config.js
module.exports = {
  output: "standalone",
  experimental: {
    outputStandalone: true,
  },
};
```

### 3. Docker Compose (Local Development)

```yaml
# docker-compose.yml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: todo-postgres
    environment:
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_password
      POSTGRES_DB: todo_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todo_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo-backend
    environment:
      DATABASE_URL: postgresql://todo_user:todo_password@postgres:5432/todo_db
      BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET}
      CORS_ORIGINS: '["http://localhost:3000"]'
      DEBUG: "true"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app  # Hot reload in development
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: base  # Use base stage for development
    container_name: todo-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      BETTER_AUTH_SECRET: ${BETTER_AUTH_SECRET}
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
```

---

## Kubernetes Deployment

### 4. Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
  labels:
    app: todo-backend
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: registry.digitalocean.com/your-registry/todo-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: auth-secret
        - name: CORS_ORIGINS
          value: '["https://todo.example.com"]'
        - name: DEBUG
          value: "false"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: todo-backend-service
  namespace: todo-app
spec:
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 5. Frontend Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  namespace: todo-app
  labels:
    app: todo-frontend
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: registry.digitalocean.com/your-registry/todo-frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.todo.example.com"
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: auth-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend-service
  namespace: todo-app
spec:
  selector:
    app: todo-frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
  type: ClusterIP
```

### 6. Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.example.com
    - api.todo.example.com
    secretName: todo-tls
  rules:
  - host: todo.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend-service
            port:
              number: 3000
  - host: api.todo.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-backend-service
            port:
              number: 8000
```

### 7. Secrets Management

```yaml
# k8s/secrets.yaml (for development - use Sealed Secrets in production)
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
  namespace: todo-app
type: Opaque
stringData:
  database-url: "postgresql://user:password@host:5432/db?sslmode=require"
  auth-secret: "your-secret-key-minimum-32-characters-long"
```

**Production: Use Sealed Secrets**:
```bash
# Install kubeseal CLI
brew install kubeseal

# Create sealed secret
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=auth-secret="..." \
  --dry-run=client -o yaml | \
  kubeseal --format yaml > sealed-secrets.yaml

# Apply sealed secret
kubectl apply -f sealed-secrets.yaml
```

---

## Helm Chart

### 8. Helm Chart Structure

```
helm/todo-app/
├── Chart.yaml
├── values.yaml
├── values-production.yaml
├── values-staging.yaml
└── templates/
    ├── namespace.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── ingress.yaml
    ├── secrets.yaml
    ├── configmap.yaml
    └── hpa.yaml
```

**Chart.yaml**:
```yaml
apiVersion: v2
name: todo-app
description: Evolution of Todo - Cloud Native Application
version: 2.0.0
appVersion: "2.0"
keywords:
  - todo
  - fastapi
  - nextjs
maintainers:
  - name: Your Name
    email: your@email.com
```

**values.yaml**:
```yaml
# Default values for todo-app
namespace: todo-app

backend:
  image:
    repository: registry.digitalocean.com/your-registry/todo-backend
    tag: latest
    pullPolicy: Always

  replicas: 2

  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

  env:
    DEBUG: "false"
    CORS_ORIGINS: '["https://todo.example.com"]'

frontend:
  image:
    repository: registry.digitalocean.com/your-registry/todo-frontend
    tag: latest
    pullPolicy: Always

  replicas: 2

  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

  env:
    NEXT_PUBLIC_API_URL: "https://api.todo.example.com"

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          service: frontend
    - host: api.todo.example.com
      paths:
        - path: /
          service: backend
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com
        - api.todo.example.com

secrets:
  databaseUrl: "postgresql://..."
  authSecret: "..."
```

**Deploy with Helm**:
```bash
# Install/upgrade
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-production.yaml \
  --namespace todo-app \
  --create-namespace

# Rollback
helm rollback todo-app

# Uninstall
helm uninstall todo-app --namespace todo-app
```

---

## CI/CD Pipeline

### 9. GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com
  REGISTRY_NAME: your-registry

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install backend dependencies
        run: |
          cd backend
          pip install uv
          uv pip install -e .

      - name: Run backend tests
        run: |
          cd backend
          pytest

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "20"

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run frontend tests
        run: |
          cd frontend
          npm test

  build-backend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}

      - name: Log in to DigitalOcean Container Registry
        run: doctl registry login

      - name: Build and push backend
        run: |
          docker build -t $REGISTRY/$REGISTRY_NAME/todo-backend:${{ github.sha }} \
                       -t $REGISTRY/$REGISTRY_NAME/todo-backend:latest \
                       ./backend
          docker push $REGISTRY/$REGISTRY_NAME/todo-backend:${{ github.sha }}
          docker push $REGISTRY/$REGISTRY_NAME/todo-backend:latest

  build-frontend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}

      - name: Log in to DigitalOcean Container Registry
        run: doctl registry login

      - name: Build and push frontend
        run: |
          docker build -t $REGISTRY/$REGISTRY_NAME/todo-frontend:${{ github.sha }} \
                       -t $REGISTRY/$REGISTRY_NAME/todo-frontend:latest \
                       ./frontend
          docker push $REGISTRY/$REGISTRY_NAME/todo-frontend:${{ github.sha }}
          docker push $REGISTRY/$REGISTRY_NAME/todo-frontend:latest

  deploy:
    needs: [build-backend, build-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}

      - name: Save DigitalOcean kubeconfig
        run: doctl kubernetes cluster kubeconfig save ${{ secrets.CLUSTER_NAME }}

      - name: Deploy with Helm
        run: |
          helm upgrade --install todo-app ./helm/todo-app \
            -f ./helm/todo-app/values-production.yaml \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --namespace todo-app \
            --create-namespace \
            --wait

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/todo-backend -n todo-app
          kubectl rollout status deployment/todo-frontend -n todo-app
```

---

## Monitoring & Logging

### 10. Prometheus Monitoring

```yaml
# k8s/monitoring/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-backend-metrics
  namespace: todo-app
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

**Add metrics to FastAPI**:
```python
# backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)
```

### 11. Grafana Dashboards

```yaml
# k8s/monitoring/grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-dashboard
  namespace: monitoring
data:
  todo-dashboard.json: |
    {
      "dashboard": {
        "title": "Todo App Metrics",
        "panels": [
          {
            "title": "Request Rate",
            "targets": [
              {
                "expr": "rate(http_requests_total{app=\"todo-backend\"}[5m])"
              }
            ]
          },
          {
            "title": "Response Time",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
              }
            ]
          }
        ]
      }
    }
```

---

## Auto-Scaling

### 12. Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

## Disaster Recovery

### 13. Database Backups

```yaml
# k8s/cronjob-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: todo-app
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump $DATABASE_URL | gzip > /backups/backup-$(date +%Y%m%d-%H%M%S).sql.gz
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: todo-secrets
                  key: database-url
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

---

## Cost Optimization

### DigitalOcean Resource Sizing
```yaml
# Production cluster (estimated $150/month)
Cluster: 3 nodes x $40/month = $120/month
  - 2 vCPU, 4GB RAM per node
LoadBalancer: $12/month
Registry: $5/month (50GB)
Neon DB: Free tier (or $19/month for pro)

Total: ~$137-156/month
```

---

## Deployment Checklist

- [ ] Docker images built and pushed
- [ ] Secrets created in Kubernetes
- [ ] Database migrated (Alembic)
- [ ] Ingress configured with SSL
- [ ] DNS records pointed to LoadBalancer
- [ ] Monitoring dashboards configured
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline tested
- [ ] Rollback procedure documented
- [ ] Load testing completed

---

## References

- DigitalOcean Kubernetes: https://www.digitalocean.com/products/kubernetes
- Helm: https://helm.sh/docs/
- cert-manager: https://cert-manager.io/
- Prometheus Operator: https://prometheus-operator.dev/

---

**Intelligence Captured**: January 2026
**Ready For**: Phase IV (Kubernetes), Phase V (Scale & Observability)
