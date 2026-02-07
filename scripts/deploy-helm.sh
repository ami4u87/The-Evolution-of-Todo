#!/bin/bash
# =============================================================================
# Deploy Todo App with Helm
# =============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHART_PATH="$PROJECT_ROOT/helm/todo-app"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
NAMESPACE="${NAMESPACE:-todo-app}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "Deploying Todo App with Helm"
echo "=============================================="

# Check required environment variables
check_env() {
    if [ -z "${!1}" ]; then
        echo -e "${RED}Error: $1 environment variable is required${NC}"
        echo "Please set it before running this script:"
        echo "  export $1=\"your-value\""
        exit 1
    fi
}

# Check prerequisites
echo "Checking prerequisites..."
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm is required but not installed.${NC}" >&2; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl is required but not installed.${NC}" >&2; exit 1; }

# Check required secrets
echo "Checking required environment variables..."
check_env "DATABASE_URL"
check_env "BETTER_AUTH_SECRET"

# Optional: GROQ_API_KEY (for AI features)
if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}Warning: GROQ_API_KEY not set. AI chat features will be disabled.${NC}"
fi

echo ""
echo "Configuration:"
echo "  Release: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Chart: $CHART_PATH"
echo ""

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Lint the chart
echo "Linting Helm chart..."
helm lint "$CHART_PATH"
echo ""

# Deploy with Helm
echo "Deploying with Helm..."
helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
    --namespace "$NAMESPACE" \
    --set secrets.databaseUrl="$DATABASE_URL" \
    --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
    --set secrets.groqApiKey="${GROQ_API_KEY:-}" \
    --set secrets.openaiApiKey="${OPENAI_API_KEY:-}" \
    --wait \
    --timeout 5m

echo ""
echo -e "${GREEN}=============================================="
echo "Deployment Complete!"
echo "==============================================${NC}"
echo ""

# Show deployment status
echo "Pod Status:"
kubectl get pods -n "$NAMESPACE" -l "app.kubernetes.io/name=todo-app"
echo ""

echo "Services:"
kubectl get svc -n "$NAMESPACE"
echo ""

echo "Ingress:"
kubectl get ingress -n "$NAMESPACE"
echo ""

# Add to /etc/hosts reminder
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
echo "4. To uninstall:"
echo "   helm uninstall $RELEASE_NAME -n $NAMESPACE"
