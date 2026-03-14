#!/usr/bin/env bash
# =============================================================================
# FlowTodo — Teardown Script
# Removes the Helm release and optionally uninstalls Dapr and stops Minikube
#
# Usage: bash scripts/teardown.sh [--all] [--stop-minikube]
#   --all            : Also uninstall Dapr from the cluster
#   --stop-minikube  : Also stop Minikube after teardown
# =============================================================================
set -e

RELEASE_NAME="flowtodo"
NAMESPACE="default"
UNINSTALL_DAPR=false
STOP_MINIKUBE=false

for arg in "$@"; do
  case $arg in
    --all) UNINSTALL_DAPR=true ;;
    --stop-minikube) STOP_MINIKUBE=true ;;
  esac
done

echo "============================================================"
echo " FlowTodo — Teardown"
echo "============================================================"

# ── Remove Helm release ─────────────────────────────────────────
echo ""
echo "[1] Uninstalling Helm release '${RELEASE_NAME}'..."
if helm status "${RELEASE_NAME}" -n "${NAMESPACE}" &>/dev/null; then
  helm uninstall "${RELEASE_NAME}" -n "${NAMESPACE}"
  echo "  Release uninstalled."
else
  echo "  Release '${RELEASE_NAME}' not found (already removed)."
fi

# ── Optionally uninstall Dapr ───────────────────────────────────
if [ "$UNINSTALL_DAPR" = true ]; then
  echo ""
  echo "[2] Uninstalling Dapr from Kubernetes..."
  dapr uninstall --kubernetes
  echo "  Dapr uninstalled."
else
  echo ""
  echo "[2] Skipping Dapr uninstall (pass --all to also remove Dapr)."
fi

# ── Optionally stop Minikube ────────────────────────────────────
if [ "$STOP_MINIKUBE" = true ]; then
  echo ""
  echo "[3] Stopping Minikube..."
  minikube stop
  echo "  Minikube stopped."
else
  echo ""
  echo "[3] Skipping Minikube stop (pass --stop-minikube to stop)."
fi

echo ""
echo "============================================================"
echo " Teardown complete."
echo " To redeploy: bash scripts/deploy.sh"
echo "============================================================"
