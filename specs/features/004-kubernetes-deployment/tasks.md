# Phase IV: Kubernetes Deployment - Task List

## Phase 1: Setup & Dockerfiles

### 1.1 Create Docker Directory Structure
- [X] Create `/docker/backend/` directory
- [X] Create `/docker/frontend/` directory

### 1.2 Backend Dockerfile (Production)
- [X] Create multi-stage Dockerfile for FastAPI
- [X] Use UV package manager for dependencies
- [X] Optimize for small image size
- [X] Configure for Neon PostgreSQL SSL

### 1.3 Frontend Dockerfile (Production)
- [X] Create multi-stage Dockerfile for Next.js
- [X] Build static assets in builder stage
- [X] Use standalone output mode
- [X] Optimize for production

## Phase 2: Helm Chart

### 2.1 Chart Structure
- [X] Create `/helm/todo-app/` directory
- [X] Create Chart.yaml with metadata
- [X] Create values.yaml with defaults
- [X] Create values-production.yaml

### 2.2 Helm Templates
- [X] Create `_helpers.tpl` with template functions
- [X] Create `namespace.yaml`
- [X] Create `secrets.yaml` for sensitive data
- [X] Create `configmap.yaml` for configuration

### 2.3 Backend Templates
- [X] Create `backend-deployment.yaml`
- [X] Create `backend-service.yaml`
- [X] Configure health checks and probes

### 2.4 Frontend Templates
- [X] Create `frontend-deployment.yaml`
- [X] Create `frontend-service.yaml`
- [X] Configure health checks and probes

### 2.5 Networking
- [X] Create `ingress.yaml` for traffic routing
- [X] Configure path-based routing

### 2.6 Scaling
- [X] Create `hpa.yaml` for auto-scaling

## Phase 3: Raw Kubernetes Manifests

### 3.1 Create K8s Directory
- [X] Create `/k8s/` directory

### 3.2 Core Manifests
- [X] Create `namespace.yaml`
- [X] Create `secrets.yaml`
- [X] Create `configmap.yaml`

### 3.3 Backend Manifests
- [X] Create `backend-deployment.yaml`
- [X] Create `backend-service.yaml`

### 3.4 Frontend Manifests
- [X] Create `frontend-deployment.yaml`
- [X] Create `frontend-service.yaml`

### 3.5 Ingress
- [X] Create `ingress.yaml`

## Phase 4: Deployment Scripts

### 4.1 Build Scripts
- [X] Create `scripts/build-images.sh`

### 4.2 Deploy Scripts
- [X] Create `scripts/deploy-helm.sh`
- [X] Create `scripts/deploy-kubectl.sh`

## Phase 5: Documentation

### 5.1 Deployment Guide
- [X] Create `/docs/kubernetes-deployment.md`
- [X] Document prerequisites
- [X] Document deployment steps
- [X] Document troubleshooting

### 5.2 Update Root README
- [X] Add Phase IV section
- [X] Link to deployment docs

## Validation Checklist

- [ ] Docker images build successfully
- [ ] Helm lint passes
- [ ] Helm template renders correctly
- [ ] kubectl apply works with raw manifests
- [ ] Application accessible via ingress
- [ ] Backend connects to Neon PostgreSQL
- [ ] Frontend can communicate with backend
- [ ] Authentication flow works
- [ ] Task CRUD operations work
- [ ] AI chatbot responds correctly
