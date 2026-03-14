#!/usr/bin/env bash
# =============================================================================
# FlowTodo — Full Local Deployment Script
# Deploys to Minikube with Full Dapr: Pub/Sub, State, Bindings, Secrets, Service Invocation
#
# Prerequisites: minikube, kubectl, helm, dapr CLI, docker (Docker Desktop WSL integration)
# Usage: bash scripts/deploy.sh [--skip-build] [--skip-dapr-init]
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHART_DIR="${PROJECT_ROOT}/todo-chatbot"
VALUES_LOCAL="${CHART_DIR}/values-local.yaml"
RELEASE_NAME="flowtodo"
NAMESPACE="default"
# Full Helm-generated service names: {release}-{chart}-{component}
BACKEND_SVC="${RELEASE_NAME}-todo-chatbot-backend"
FRONTEND_SVC="${RELEASE_NAME}-todo-chatbot-frontend"

# Parse args
SKIP_BUILD=false
SKIP_DAPR_INIT=false
for arg in "$@"; do
  case $arg in
    --skip-build) SKIP_BUILD=true ;;
    --skip-dapr-init) SKIP_DAPR_INIT=true ;;
  esac
done

echo "============================================================"
echo " FlowTodo — Minikube + Dapr Deployment"
echo "============================================================"

# ── Docker availability check ───────────────────────────────────
# Docker Desktop WSL integration may not be set up — try both
if ! command -v docker &>/dev/null; then
  DOCKER_EXE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
  if [ -f "$DOCKER_EXE" ]; then
    echo "  docker not in PATH — using Docker Desktop exe directly"
    export PATH="$PATH:/mnt/c/Program Files/Docker/Docker/resources/bin"
    # Also ensure docker.exe is callable as 'docker'
    mkdir -p /tmp/docker-bin
    ln -sf "$DOCKER_EXE" /tmp/docker-bin/docker 2>/dev/null || true
    export PATH="/tmp/docker-bin:$PATH"
  else
    echo "  ERROR: Docker not found. Enable Docker Desktop WSL integration:"
    echo "  Docker Desktop → Settings → Resources → WSL Integration → enable distro"
    exit 1
  fi
fi

# Verify docker works
if ! docker info &>/dev/null; then
  echo ""
  echo "  ERROR: Docker daemon not reachable."
  echo "  Make sure Docker Desktop is running and WSL integration is enabled."
  exit 1
fi

# ── Step 1: Start Minikube ──────────────────────────────────────
echo ""
echo "[1/7] Starting Minikube..."
if minikube status 2>/dev/null | grep -q "Running"; then
  echo "  Minikube already running."
else
  minikube start --cpus=4 --memory=8192 --driver=docker
  echo "  Minikube started."
fi

# ── Step 2: Initialize Dapr on Kubernetes ──────────────────────
echo ""
echo "[2/7] Initializing Dapr on Kubernetes..."
if [ "$SKIP_DAPR_INIT" = true ]; then
  echo "  Skipping Dapr init (--skip-dapr-init passed)."
else
  DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | grep -c "Running" || echo "0")
  if [ "$DAPR_PODS" -ge 3 ]; then
    echo "  Dapr already initialized ($DAPR_PODS pods running)."
  else
    echo "  Running dapr init --kubernetes --wait ..."
    dapr init --kubernetes --wait
    echo "  Dapr initialized."
  fi
fi

echo "  Waiting for Dapr control plane to be ready..."
kubectl wait --for=condition=Ready pod -l app=dapr-operator \
  -n dapr-system --timeout=120s 2>/dev/null && echo "  Dapr operator ready." || \
echo "  (continuing — Dapr may already be ready)"

# Label default namespace for Dapr sidecar injection
kubectl label namespace ${NAMESPACE} dapr-injection=enabled --overwrite 2>/dev/null || true

# ── Step 3: Build Docker images inside Minikube ────────────────
echo ""
echo "[3/7] Building Docker images in Minikube daemon..."
if [ "$SKIP_BUILD" = true ]; then
  echo "  Skipping image build (--skip-build passed)."
else
  eval "$(minikube docker-env)"
  echo "  Building backend image..."
  docker build -t hackathon-backend:latest "${PROJECT_ROOT}/backend"
  echo "  Building frontend image..."
  docker build -t hackathon-frontend:latest "${PROJECT_ROOT}/frontend"
  echo "  Images built successfully."
fi

# ── Step 4: Check values-local.yaml ────────────────────────────
echo ""
echo "[4/7] Checking configuration..."
if [ ! -f "${VALUES_LOCAL}" ]; then
  echo ""
  echo "  ERROR: ${VALUES_LOCAL} not found."
  echo "  Copy todo-chatbot/values-local.example.yaml to todo-chatbot/values-local.yaml"
  echo "  and fill in your real secrets before deploying."
  exit 1
fi
echo "  values-local.yaml found."

# ── Step 5: Update Helm dependencies ───────────────────────────
echo ""
echo "[5/7] Updating Helm dependencies (Redis chart)..."
cd "${CHART_DIR}"
helm dependency update . 2>&1 | grep -v "^Getting updates" || true
cd "${PROJECT_ROOT}"
echo "  Dependencies ready."

# ── Step 6: Deploy with Helm ────────────────────────────────────
echo ""
echo "[6/7] Deploying FlowTodo with Helm..."
helm upgrade --install "${RELEASE_NAME}" "${CHART_DIR}" \
  -f "${VALUES_LOCAL}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --wait \
  --timeout 8m
echo "  Helm release '${RELEASE_NAME}' deployed successfully."

# ── Step 7: Verify & print URLs ────────────────────────────────
echo ""
echo "[7/7] Verifying deployment..."
echo ""
echo "  All pods in namespace '${NAMESPACE}':"
kubectl get pods -n "${NAMESPACE}"
echo ""
echo "  Dapr control plane (dapr-system):"
kubectl get pods -n dapr-system 2>/dev/null || echo "  (dapr-system namespace not found)"

echo ""
echo "============================================================"
echo " Deployment complete!"
echo "============================================================"
echo ""
echo " Getting service URLs..."
echo ""

FRONTEND_URL=$(minikube service "${FRONTEND_SVC}" --url -n "${NAMESPACE}" 2>/dev/null || echo "  Run: minikube service ${FRONTEND_SVC} --url")
BACKEND_URL=$(minikube service "${BACKEND_SVC}" --url -n "${NAMESPACE}" 2>/dev/null || echo "  Run: minikube service ${BACKEND_SVC} --url")

echo " Frontend:      ${FRONTEND_URL}"
echo " Backend API:   ${BACKEND_URL}"
echo " API Docs:      ${BACKEND_URL}/docs"
echo ""
echo " Zipkin tracing:"
echo "   kubectl port-forward svc/zipkin 9411:9411 &"
echo "   open http://localhost:9411"
echo ""
echo " Verify Dapr building blocks:"
echo "   kubectl logs -l app.kubernetes.io/component=backend -c backend -f"
