#!/bin/bash
# =============================================================================
# Setup Prerequisites for DigitalOcean Kubernetes (DOKS)
# Installs: Strimzi Kafka Operator, Dapr, NGINX Ingress, cert-manager
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "Setting up DOKS Prerequisites"
echo "=============================================="

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl required${NC}" >&2; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm required${NC}" >&2; exit 1; }

# Verify cluster connection
echo "Verifying cluster connection..."
kubectl cluster-info || { echo -e "${RED}Error: Cannot connect to cluster${NC}" >&2; exit 1; }
echo ""

# 1. Install NGINX Ingress Controller
echo -e "${GREEN}[1/4] Installing NGINX Ingress Controller...${NC}"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>/dev/null || true
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx --create-namespace \
    --set controller.publishService.enabled=true \
    --wait --timeout 5m
echo ""

# 2. Install cert-manager (for TLS)
echo -e "${GREEN}[2/4] Installing cert-manager...${NC}"
helm repo add jetstack https://charts.jetstack.io 2>/dev/null || true
helm repo update
helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager --create-namespace \
    --set crds.enabled=true \
    --wait --timeout 5m
echo ""

# 3. Install Strimzi Kafka Operator
echo -e "${GREEN}[3/4] Installing Strimzi Kafka Operator...${NC}"
helm repo add strimzi https://strimzi.io/charts/ 2>/dev/null || true
helm repo update
helm upgrade --install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
    --namespace kafka --create-namespace \
    --wait --timeout 5m
echo ""

# Wait for Strimzi operator to be ready
echo "Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=120s

# Deploy Kafka cluster
echo "Deploying Kafka cluster..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
kubectl apply -f "$PROJECT_ROOT/k8s/kafka/kafka-cluster.yaml"
kubectl apply -f "$PROJECT_ROOT/k8s/kafka/kafka-topic.yaml"

echo "Waiting for Kafka cluster to be ready (this may take 2-5 minutes)..."
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka || \
    echo -e "${YELLOW}Kafka still starting, continue setup and check later${NC}"
echo ""

# 4. Install Dapr
echo -e "${GREEN}[4/4] Installing Dapr...${NC}"
helm repo add dapr https://dapr.github.io/helm-charts/ 2>/dev/null || true
helm repo update
helm upgrade --install dapr dapr/dapr \
    --namespace dapr-system --create-namespace \
    --wait --timeout 5m
echo ""

echo -e "${GREEN}=============================================="
echo "Prerequisites Installation Complete!"
echo "==============================================${NC}"
echo ""
echo "Installed:"
echo "  1. NGINX Ingress Controller (ingress-nginx namespace)"
echo "  2. cert-manager (cert-manager namespace)"
echo "  3. Strimzi Kafka Operator + Cluster (kafka namespace)"
echo "  4. Dapr (dapr-system namespace)"
echo ""
echo "Next steps:"
echo "  1. Wait for Kafka to be ready:"
echo "     kubectl wait kafka/todo-kafka --for=condition=Ready -n kafka --timeout=300s"
echo "  2. Deploy the application:"
echo "     ./scripts/deploy-doks.sh"
