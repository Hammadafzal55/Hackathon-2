#!/usr/bin/env bash
# =============================================================================
# Phase-4: Todo Chatbot — Minikube Deployment Script
# =============================================================================
# Usage:
#   ./deploy-minikube.sh [--delete] [--skip-build] [--help]
#
# Prerequisites:
#   - Fill in todo-chatbot/values.local.yaml (REPLACE_ME placeholders)
#   - minikube, helm, kubectl, docker installed
# =============================================================================

set -euo pipefail

CHART_DIR="$(cd "$(dirname "$0")/todo-chatbot" && pwd)"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VALUES_LOCAL="$CHART_DIR/values.local.yaml"
RELEASE_NAME="todo"
NAMESPACE="default"
FRONTEND_IMAGE="hackathon-frontend:latest"
BACKEND_IMAGE="hackathon-backend:latest"
SKIP_BUILD=false
DELETE_RELEASE=false

# ── Argument parsing ─────────────────────────────────────────────────────────
for arg in "$@"; do
  case $arg in
    --delete)   DELETE_RELEASE=true ;;
    --skip-build) SKIP_BUILD=true ;;
    --help)
      echo "Usage: $0 [--delete] [--skip-build]"
      echo "  --delete      Uninstall existing Helm release and exit"
      echo "  --skip-build  Skip Docker image builds (reuse existing images)"
      exit 0
      ;;
  esac
done

# ── Colour helpers ───────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ── Check prerequisites ───────────────────────────────────────────────────────
for cmd in minikube helm kubectl docker; do
  command -v "$cmd" &>/dev/null || error "$cmd is not installed"
done

# ── Check values.local.yaml ───────────────────────────────────────────────────
[[ -f "$VALUES_LOCAL" ]] || error "Missing $VALUES_LOCAL — copy and fill the template first"
if grep -q "REPLACE_ME" "$VALUES_LOCAL"; then
  error "Found REPLACE_ME placeholders in $VALUES_LOCAL — fill in your secrets before deploying"
fi

# ── Delete mode ───────────────────────────────────────────────────────────────
if $DELETE_RELEASE; then
  info "Uninstalling Helm release '$RELEASE_NAME'..."
  helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || true
  success "Release uninstalled"
  exit 0
fi

# ── 1. Start Minikube ─────────────────────────────────────────────────────────
info "Checking Minikube status..."
if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
  info "Starting Minikube..."
  minikube start --driver=docker --cpus=2 --memory=3072
  success "Minikube started"
else
  success "Minikube is already running"
fi

# ── 2. Get Minikube IP ────────────────────────────────────────────────────────
MINIKUBE_IP="$(minikube ip)"
BACKEND_URL="http://${MINIKUBE_IP}:30800"
FRONTEND_URL="http://${MINIKUBE_IP}:30300"
info "Minikube IP: $MINIKUBE_IP"
info "Backend URL: $BACKEND_URL"
info "Frontend URL: $FRONTEND_URL"

# ── 3. Point Docker to Minikube's daemon ──────────────────────────────────────
info "Configuring Docker to use Minikube's daemon..."
eval "$(minikube docker-env)"
success "Docker now points to Minikube"

# ── 4. Build Docker images ────────────────────────────────────────────────────
if ! $SKIP_BUILD; then
  info "Building backend image: $BACKEND_IMAGE"
  docker build \
    -t "$BACKEND_IMAGE" \
    "$ROOT_DIR/backend"
  success "Backend image built"

  # Use localhost URLs for browser access (via port-forward) — NOT minikube IP
  info "Building frontend image: $FRONTEND_IMAGE (API URL: http://localhost:8000)"
  docker build \
    --build-arg "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" \
    --build-arg "NEXT_PUBLIC_APP_URL=http://localhost:3000" \
    -t "$FRONTEND_IMAGE" \
    "$ROOT_DIR/frontend"
  success "Frontend image built"
else
  warn "Skipping image builds (--skip-build)"
fi

# ── 5. Update ALLOWED_ORIGINS in values.local.yaml ───────────────────────────
info "Patching ALLOWED_ORIGINS in $VALUES_LOCAL ..."
# Build JSON array string for allowed origins
ORIGINS='["http://localhost:3000","'"${FRONTEND_URL}"'"]'
# Use Python to safely update the YAML value
python3 - <<PYEOF
import re, pathlib
path = pathlib.Path("$VALUES_LOCAL")
content = path.read_text()
new_line = "    ALLOWED_ORIGINS: '${ORIGINS}'"
content = re.sub(r"^\s+ALLOWED_ORIGINS:.*$", new_line, content, flags=re.MULTILINE)
path.write_text(content)
PYEOF
success "ALLOWED_ORIGINS updated to: $ORIGINS"

# ── 6. Also update BETTER_AUTH_URL and NEXT_PUBLIC_APP_URL in frontend env ───
info "Patching frontend BETTER_AUTH_URL in $VALUES_LOCAL ..."
python3 - <<PYEOF
import re, pathlib
path = pathlib.Path("$VALUES_LOCAL")
content = path.read_text()
for pattern, replacement in [
    (r"^\s+BETTER_AUTH_URL:.*$", "    BETTER_AUTH_URL: '${FRONTEND_URL}'"),
    (r"^\s+NEXT_PUBLIC_APP_URL:.*$", "    NEXT_PUBLIC_APP_URL: '${FRONTEND_URL}'"),
    (r"^\s+NEXT_PUBLIC_API_BASE_URL:.*$", "    NEXT_PUBLIC_API_BASE_URL: '${BACKEND_URL}'"),
]:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
path.write_text(content)
PYEOF

# ── 7. Helm deploy ────────────────────────────────────────────────────────────
info "Deploying Helm chart '$RELEASE_NAME'..."
helm upgrade --install "$RELEASE_NAME" "$CHART_DIR" \
  -f "$CHART_DIR/values.yaml" \
  -f "$VALUES_LOCAL" \
  --namespace "$NAMESPACE" \
  --wait \
  --timeout 5m

success "Helm release '$RELEASE_NAME' deployed"

# ── 8. Status ─────────────────────────────────────────────────────────────────
echo ""
info "Pod status:"
kubectl get pods -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME"

echo ""
info "Services:"
kubectl get svc -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME"

echo ""
success "==================================================================="
success "Deployment complete!"
echo -e "  Frontend: ${GREEN}${FRONTEND_URL}${NC}"
echo -e "  Backend:  ${GREEN}${BACKEND_URL}${NC}"
echo -e "  API docs: ${GREEN}${BACKEND_URL}/docs${NC}"
success "==================================================================="
echo ""
info "To open the frontend in your browser:"
echo "  minikube service ${RELEASE_NAME}-todo-chatbot-frontend -n $NAMESPACE"
echo ""
info "To follow logs:"
echo "  kubectl logs -l app.kubernetes.io/component=frontend -f"
echo "  kubectl logs -l app.kubernetes.io/component=backend -f"
echo ""
info "To uninstall:"
echo "  $0 --delete"
