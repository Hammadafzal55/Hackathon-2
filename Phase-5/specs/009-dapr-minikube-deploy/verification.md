# Verification Guide: Dapr Minikube Deployment

**Feature**: 009-dapr-minikube-deploy
**Status**: Implementation complete — manual verification required after `bash scripts/deploy.sh`

---

## Pre-Verification Checklist

Before verifying, ensure:
- [ ] `bash scripts/deploy.sh` completed without errors
- [ ] `kubectl get pods` shows all pods in `Running` state
- [ ] `kubectl get pods -n dapr-system` shows Dapr control plane pods `Running`

---

## Building Block Verification

### 1. Basic Deployment (US1)

```bash
# All pods should be Running
kubectl get pods

# Expected pods (all Running):
# flowtodo-backend-xxx        2/2   Running   (2/2 = app + daprd sidecar)
# flowtodo-frontend-xxx       1/1   Running
# flowtodo-redis-master-0     1/1   Running
# zipkin-xxx                  1/1   Running

# Dapr control plane
kubectl get pods -n dapr-system
# Expected: dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement-server
```

**Pass criteria**: `2/2` for backend pod ✓

---

### 2. Pub/Sub (US2)

```bash
# Create a task (get a JWT token from login first)
TOKEN="your-jwt-token-here"
BACKEND_URL=$(minikube service flowtodo-backend --url)
curl -s -X POST "${BACKEND_URL}/api/tasks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Pub/Sub task", "status": "pending", "priority": 3}' | python3 -m json.tool

# Check backend published the event
kubectl logs -l app.kubernetes.io/component=backend -c backend | grep -i "published\|task.created"

# Check subscriber received the event
kubectl logs -l app.kubernetes.io/component=backend -c backend | grep -i "task-events\|received task"
```

**Pass criteria**: "Published task.created event" in logs + notification visible in UI ✓

---

### 3. Cron Bindings (US3)

```bash
# Watch logs for cron invocations (wait up to 60 seconds)
kubectl logs -l app.kubernetes.io/component=backend -c backend -f | grep -i "cron\|check-reminders\|generate-recurrences"
```

**Pass criteria**: `/cron/check-reminders` called every ~60s in logs ✓

---

### 4. Secrets Store (US4)

```bash
# Check backend loaded secrets from Dapr
kubectl logs -l app.kubernetes.io/component=backend -c backend | grep -i "secret\|dapr"
# Expected: "Secrets loaded from Dapr Secrets Store: ['DATABASE_URL', ...]"
```

**Pass criteria**: "Secrets loaded from Dapr Secrets Store" in startup logs ✓

---

### 5. Service Invocation + Zipkin (US5)

```bash
# Start Zipkin port-forward
kubectl port-forward svc/zipkin 9411:9411 &

# Get auth token and call the test endpoint
TOKEN="your-jwt-token-here"
BACKEND_URL=$(minikube service flowtodo-backend --url)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "${BACKEND_URL}/api/dapr/self-invoke-test" | python3 -m json.tool

# Expected response:
# {
#   "status": "ok",
#   "message": "Dapr Service Invocation with mTLS succeeded",
#   "dapr_app_id": "flowtodo-backend",
#   "invocation_result": {"status": "healthy", ...},
#   "hint": "Check Zipkin at http://localhost:9411 for the distributed trace"
# }

# View trace in Zipkin
open http://localhost:9411
# Search: service = flowtodo-backend
# Find trace with 2 spans (client + server)
```

**Pass criteria**: 200 response + 2-span trace in Zipkin ✓

---

## Reproducibility Test

```bash
bash scripts/teardown.sh
bash scripts/deploy.sh
# All pods should reach Running again within 5 minutes
```

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Backend pod `1/2` (not `2/2`) | Dapr sidecar not injected | Check `dapr-sidecar-injector` pod in dapr-system; re-annotate namespace |
| Pub/Sub events not appearing | Redis pod not ready | `kubectl get pod flowtodo-redis-master-0` |
| Cron not firing | Binding component not applied | `kubectl get component` |
| "Secrets loaded from env" (not Dapr) | Dapr sidecar not ready at startup | Restart backend pod: `kubectl rollout restart deployment flowtodo-backend` |
| Zipkin shows no traces | Tracing config not applied | `kubectl get configuration appconfig` |
| `helm install` fails on Dapr CRDs | Dapr not initialized | Run `dapr init --kubernetes --wait` first |
