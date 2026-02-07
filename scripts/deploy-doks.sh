#!/bin/bash
# =============================================================================
# Deploy Todo App to DigitalOcean Kubernetes (DOKS)
# =============================================================================
# Prerequisites: Run ./scripts/setup-doks-prereqs.sh first
#
# Required environment variables:
#   DATABASE_URL        - Neon PostgreSQL connection string
#   BETTER_AUTH_SECRET  - JWT signing secret (min 32 chars)
#   DO_REGISTRY         - DigitalOcean container registry name
#
# Optional:
#   GROQ_API_KEY        - Groq API key for AI chat
#   DOMAIN              - Custom domain (default: todo.yourdomain.com)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHART_PATH="$PROJECT_ROOT/helm/todo-app"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
NAMESPACE="${NAMESPACE:-todo-app}"
DO_REGISTRY="${DO_REGISTRY:-todo-app}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "Deploying Todo App to DOKS"
echo "=============================================="

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl required${NC}" >&2; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm required${NC}" >&2; exit 1; }
command -v doctl >/dev/null 2>&1 || { echo -e "${YELLOW}Warning: doctl not found, skipping registry auth${NC}"; }

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL is required${NC}"
    echo "  export DATABASE_URL='postgresql://...'"
    exit 1
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo -e "${RED}Error: BETTER_AUTH_SECRET is required${NC}"
    echo "  export BETTER_AUTH_SECRET='your-secret-min-32-chars'"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  Release:   $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Registry:  registry.digitalocean.com/$DO_REGISTRY"
echo ""

# Step 1: Build and push images
echo -e "${GREEN}[1/4] Building and pushing Docker images...${NC}"
BACKEND_TAG="registry.digitalocean.com/$DO_REGISTRY/todo-backend:latest"
FRONTEND_TAG="registry.digitalocean.com/$DO_REGISTRY/todo-frontend:latest"

docker build -t "$BACKEND_TAG" -f "$PROJECT_ROOT/docker/backend/Dockerfile" "$PROJECT_ROOT"
docker build -t "$FRONTEND_TAG" -f "$PROJECT_ROOT/docker/frontend/Dockerfile" "$PROJECT_ROOT"

if command -v doctl >/dev/null 2>&1; then
    doctl registry login
fi

docker push "$BACKEND_TAG"
docker push "$FRONTEND_TAG"
echo ""

# Step 2: Create registry secret
echo -e "${GREEN}[2/4] Setting up image pull secret...${NC}"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

if command -v doctl >/dev/null 2>&1; then
    doctl registry kubernetes-manifest | kubectl apply -f -
fi
echo ""

# Step 3: Deploy Dapr pub/sub components
echo -e "${GREEN}[3/4] Deploying Dapr components...${NC}"
kubectl apply -f "$PROJECT_ROOT/k8s/dapr/dapr-pubsub-kafka.yaml"
kubectl apply -f "$PROJECT_ROOT/k8s/dapr/dapr-subscription.yaml"
echo ""

# Step 4: Deploy with Helm
echo -e "${GREEN}[4/4] Deploying with Helm...${NC}"
helm lint "$CHART_PATH"

helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
    -f "$CHART_PATH/values-doks.yaml" \
    --namespace "$NAMESPACE" \
    --set secrets.databaseUrl="$DATABASE_URL" \
    --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
    --set secrets.groqApiKey="${GROQ_API_KEY:-}" \
    --set secrets.openaiApiKey="${OPENAI_API_KEY:-}" \
    --set backend.image.repository="registry.digitalocean.com/$DO_REGISTRY/todo-backend" \
    --set frontend.image.repository="registry.digitalocean.com/$DO_REGISTRY/todo-frontend" \
    --wait \
    --timeout 5m

echo ""
echo -e "${GREEN}=============================================="
echo "DOKS Deployment Complete!"
echo "==============================================${NC}"
echo ""

# Show status
echo "Pod Status:"
kubectl get pods -n "$NAMESPACE"
echo ""

echo "Services:"
kubectl get svc -n "$NAMESPACE"
echo ""

echo "Ingress:"
kubectl get ingress -n "$NAMESPACE"
echo ""

# Get Load Balancer IP
echo "Load Balancer:"
LB_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
echo "  External IP: $LB_IP"
echo ""

echo "=============================================="
echo "Next Steps:"
echo "=============================================="
echo ""
echo "1. Point your domain to the Load Balancer IP: $LB_IP"
echo "   Add an A record: todo.yourdomain.com → $LB_IP"
echo ""
echo "2. (Optional) Enable TLS:"
echo "   Update values-doks.yaml to uncomment TLS section"
echo "   helm upgrade todo-app ./helm/todo-app -f ./helm/todo-app/values-doks.yaml ..."
echo ""
echo "3. Verify the deployment:"
echo "   curl http://$LB_IP/health"
echo ""
echo "4. Monitor events:"
echo "   kubectl logs -f deployment/todo-app-backend -n $NAMESPACE | grep 'Event:'"
echo ""
echo "5. To uninstall:"
echo "   helm uninstall $RELEASE_NAME -n $NAMESPACE"
