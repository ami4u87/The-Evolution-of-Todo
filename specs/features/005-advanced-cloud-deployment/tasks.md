# Phase V: Advanced Cloud Deployment - Task List

## Phase 1: Event System (Backend)

### 1.1 Event Models and Publisher
- [X] Create `backend/app/events/__init__.py`
- [X] Create `backend/app/events/models.py` with CloudEvents-style schema
- [X] Create `backend/app/events/topics.py` with topic constants
- [X] Create `backend/app/events/publisher.py` with Dapr pub/sub client

### 1.2 Integrate Events into Task Service
- [X] Modify `task_service.py` to emit events after CRUD operations
- [X] Add event config to `config.py` (Dapr settings)
- [X] Add health check for event system in `main.py`

### 1.3 Update Dependencies
- [X] Add `httpx` to pyproject.toml for Dapr HTTP communication
- [X] Version bump to 5.0.0

## Phase 2: Kafka Infrastructure

### 2.1 Strimzi Kafka Operator
- [X] Create `k8s/kafka/strimzi-operator.yaml` (namespace + operator install ref)
- [X] Create `k8s/kafka/kafka-cluster.yaml` (single-node for dev, multi for prod)
- [X] Create `k8s/kafka/kafka-topic.yaml` (task-events topic)

### 2.2 Dapr Components
- [X] Create `k8s/dapr/dapr-pubsub-kafka.yaml` (Dapr Component for Kafka)
- [X] Create `k8s/dapr/dapr-subscription.yaml` (subscription definitions)

## Phase 3: Helm Chart Updates

### 3.1 DOKS Values
- [X] Create `helm/todo-app/values-doks.yaml` with DO-specific config
- [X] Add Dapr annotations to backend deployment template
- [X] Create `helm/todo-app/templates/dapr-pubsub.yaml`
- [X] Add `dapr` config section to `values.yaml`
- [X] Add `EVENTS_ENABLED` to configmap template

## Phase 4: DOKS Deployment

### 4.1 Deployment Scripts
- [X] Create `scripts/setup-doks-prereqs.sh` (install Strimzi + Dapr + cert-manager)
- [X] Create `scripts/deploy-doks.sh` (full DOKS deployment)

## Phase 5: Documentation

### 5.1 Deployment Guide
- [X] Create `docs/doks-deployment.md`
- [X] Update root README.md with Phase V section

### 5.2 PHR
- [X] Create PHR for Phase V implementation
