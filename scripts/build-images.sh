#!/bin/bash
# =============================================================================
# Build Docker Images for Todo App
# =============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_TAG="${BACKEND_TAG:-todo-backend:latest}"
FRONTEND_TAG="${FRONTEND_TAG:-todo-frontend:latest}"

echo "=============================================="
echo "Building Todo App Docker Images"
echo "=============================================="
echo "Project root: $PROJECT_ROOT"
echo ""

# Build backend image
echo "Building backend image: $BACKEND_TAG"
docker build \
    -t "$BACKEND_TAG" \
    -f "$PROJECT_ROOT/docker/backend/Dockerfile" \
    "$PROJECT_ROOT"

echo ""
echo "Backend image built successfully!"
echo ""

# Build frontend image
echo "Building frontend image: $FRONTEND_TAG"
docker build \
    -t "$FRONTEND_TAG" \
    -f "$PROJECT_ROOT/docker/frontend/Dockerfile" \
    "$PROJECT_ROOT"

echo ""
echo "Frontend image built successfully!"
echo ""

echo "=============================================="
echo "Build Complete!"
echo "=============================================="
echo ""
echo "Images created:"
echo "  - $BACKEND_TAG"
echo "  - $FRONTEND_TAG"
echo ""
echo "To push to a registry:"
echo "  docker tag $BACKEND_TAG your-registry.com/todo-backend:latest"
echo "  docker push your-registry.com/todo-backend:latest"
echo ""
echo "For minikube, run:"
echo "  eval \$(minikube docker-env)"
echo "  ./scripts/build-images.sh"
