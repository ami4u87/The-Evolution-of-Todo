#!/bin/bash
# =============================================================================
# Deploy Todo App with kubectl (raw manifests)
# =============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_PATH="$PROJECT_ROOT/k8s"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "Deploying Todo App with kubectl"
echo "=============================================="

# Check prerequisites
echo "Checking prerequisites..."
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl is required but not installed.${NC}" >&2; exit 1; }

# Check required environment variables
if [ -z "$DATABASE_URL" ] || [ -z "$BETTER_AUTH_SECRET" ]; then
    echo -e "${YELLOW}Warning: Environment variables not set.${NC}"
    echo ""
    echo "You have two options:"
    echo ""
    echo "Option 1: Set environment variables and use kubectl create secret:"
    echo "  export DATABASE_URL='postgresql://...'"
    echo "  export BETTER_AUTH_SECRET='your-secret'"
    echo "  kubectl create secret generic todo-secrets \\"
    echo "    --namespace todo-app \\"
    echo "    --from-literal=DATABASE_URL=\"\$DATABASE_URL\" \\"
    echo "    --from-literal=BETTER_AUTH_SECRET=\"\$BETTER_AUTH_SECRET\" \\"
    echo "    --from-literal=GROQ_API_KEY=\"\${GROQ_API_KEY:-}\" \\"
    echo "    --from-literal=OPENAI_API_KEY=\"\${OPENAI_API_KEY:-}\""
    echo ""
    echo "Option 2: Edit k8s/secrets.yaml directly (not recommended for git)"
    echo ""
fi

echo ""
echo "Manifests path: $K8S_PATH"
echo ""

# Apply manifests in order
echo "Applying Kubernetes manifests..."
echo ""

echo "1. Creating namespace..."
kubectl apply -f "$K8S_PATH/namespace.yaml"

echo "2. Creating secrets..."
if [ -n "$DATABASE_URL" ] && [ -n "$BETTER_AUTH_SECRET" ]; then
    # Create secrets from environment variables
    kubectl create secret generic todo-secrets \
        --namespace todo-app \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
        --from-literal=GROQ_API_KEY="${GROQ_API_KEY:-}" \
        --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
        --dry-run=client -o yaml | kubectl apply -f -
else
    echo -e "${YELLOW}Applying secrets from file (make sure to edit k8s/secrets.yaml first)${NC}"
    kubectl apply -f "$K8S_PATH/secrets.yaml"
fi

echo "3. Creating configmap..."
kubectl apply -f "$K8S_PATH/configmap.yaml"

echo "4. Deploying backend..."
kubectl apply -f "$K8S_PATH/backend-deployment.yaml"
kubectl apply -f "$K8S_PATH/backend-service.yaml"

echo "5. Deploying frontend..."
kubectl apply -f "$K8S_PATH/frontend-deployment.yaml"
kubectl apply -f "$K8S_PATH/frontend-service.yaml"

echo "6. Creating ingress..."
kubectl apply -f "$K8S_PATH/ingress.yaml"

echo ""
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/todo-backend -n todo-app --timeout=5m
kubectl rollout status deployment/todo-frontend -n todo-app --timeout=5m

echo ""
echo -e "${GREEN}=============================================="
echo "Deployment Complete!"
echo "==============================================${NC}"
echo ""

# Show deployment status
echo "Pod Status:"
kubectl get pods -n todo-app
echo ""

echo "Services:"
kubectl get svc -n todo-app
echo ""

echo "Ingress:"
kubectl get ingress -n todo-app
echo ""

# Next steps
echo "=============================================="
echo "Next Steps:"
echo "=============================================="
echo ""
echo "1. Add to /etc/hosts (if using todo.local):"
echo "   echo '127.0.0.1 todo.local' | sudo tee -a /etc/hosts"
echo ""
echo "2. For minikube, enable ingress and tunnel:"
echo "   minikube addons enable ingress"
echo "   minikube tunnel"
echo ""
echo "3. Access the application:"
echo "   http://todo.local"
echo ""
echo "4. To delete all resources:"
echo "   kubectl delete -f $K8S_PATH/"
