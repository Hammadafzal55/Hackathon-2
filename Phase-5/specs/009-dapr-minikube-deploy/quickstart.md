# Quickstart: FlowTodo on Minikube with Full Dapr

**Feature**: 009-dapr-minikube-deploy
**Time to deploy**: ~5 minutes (after prerequisites installed)

---

## Prerequisites

Ensure these are installed on your machine:

```bash
# Check versions
minikube version        # >= 1.32
kubectl version         # >= 1.28
helm version            # >= 3.14
dapr --version          # >= 1.14
docker --version        # >= 24
```

Install guides (out of scope — see official docs):
- Minikube: https://minikube.sigs.k8s.io/docs/start/
- Dapr CLI: https://docs.dapr.io/getting-started/install-dapr-cli/

---

## Full Deploy (One Script)

```bash
cd /path/to/Phase-5
bash scripts/deploy.sh
```

The script handles everything:
1. Starts Minikube (8 CPUs, 8 GB RAM)
2. Initializes Dapr on Kubernetes (if not already done)
3. Builds Docker images inside Minikube's Docker daemon
4. Updates Helm dependencies (downloads Redis chart)
5. Deploys the Helm chart (creates all K8s resources + Dapr components)
6. Waits for all pods to reach `Running` state
7. Prints access URLs

---

## Step-by-Step (Manual)

### Step 1: Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Step 2: Initialize Dapr

```bash
# First time only
dapr init --kubernetes --wait
kubectl get pods -n dapr-system    # All should be Running
```

### Step 3: Build Docker Images

```bash
# Point Docker CLI at Minikube's daemon
eval $(minikube docker-env)

# Build backend
docker build -t hackathon-backend:latest ./backend

# Build frontend
docker build -t hackathon-frontend:latest ./frontend
```

### Step 4: Configure Secrets

```bash
# Create a local values override file (gitignored)
cp todo-chatbot/values-local.example.yaml todo-chatbot/values-local.yaml

# Edit values-local.yaml with your real secrets:
# secrets.databaseUrl, secrets.betterAuthSecret, secrets.jwtSecretKey, secrets.aiApiKey
```

### Step 5: Deploy with Helm

```bash
cd todo-chatbot
helm dependency update
cd ..

helm upgrade --install flowtodo ./todo-chatbot \
  -f todo-chatbot/values-local.yaml \
  --namespace default \
  --wait --timeout 5m
```

### Step 6: Verify Deployment

```bash
# All pods should show Running
kubectl get pods

# Expected pods:
# flowtodo-backend-xxx        2/2   Running  (app + daprd sidecar)
# flowtodo-frontend-xxx       1/1   Running
# flowtodo-redis-master-0     1/1   Running
# zipkin-xxx                  1/1   Running
# dapr-operator-xxx           1/1   Running   (in dapr-system)
# dapr-sidecar-injector-xxx   1/1   Running   (in dapr-system)
# dapr-sentry-xxx             1/1   Running   (in dapr-system)
# dapr-placement-server-xxx   1/1   Running   (in dapr-system)
```

---

## Access the Application

### Frontend

```bash
minikube service flowtodo-frontend --url
# Opens http://127.0.0.1:<port>
```

### Backend API

```bash
minikube service flowtodo-backend --url
# Opens http://127.0.0.1:<port>
# API docs: http://127.0.0.1:<port>/docs
```

### Zipkin (Distributed Tracing)

```bash
kubectl port-forward svc/zipkin 9411:9411 &
open http://localhost:9411
```

---

## Verify Dapr Building Blocks

### Pub/Sub

```bash
# 1. Create a task via the UI or API
# 2. Check backend logs
kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep "Published"
# Expected: "Published task.created event for task <id>"

# 3. Check subscriber received it
kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep "task-events"
# Expected: "Received task event: task.created"
```

### Cron Binding (Reminders)

```bash
# Watch cron firing every 60 seconds
kubectl logs -l app=flowtodo-backend -c flowtodo-backend -f | grep "check-reminders"
# Expected: "POST /cron/check-reminders" every 60 seconds
```

### Secrets Store

```bash
# Check backend loaded secrets from Dapr
kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep -i "secret"
# Expected: "Secrets loaded from Dapr Secrets Store"
```

### Service Invocation + Tracing

```bash
# Trigger the self-invocation test (requires auth token)
curl -H "Authorization: Bearer <token>" \
  http://$(minikube service flowtodo-backend --url)/api/dapr/self-invoke-test

# View trace in Zipkin
open http://localhost:9411
# Search for service: flowtodo-backend, look for 2-span traces
```

---

## Teardown

```bash
bash scripts/teardown.sh

# Or manual:
helm uninstall flowtodo
dapr uninstall --kubernetes
minikube stop
```

---

## Troubleshooting

### Backend pod stuck in Init state

```bash
kubectl describe pod -l app=flowtodo-backend
# Common cause: Dapr sidecar injector not ready
# Fix: wait for dapr-sidecar-injector pod to be Running in dapr-system
```

### Pub/Sub not receiving events

```bash
kubectl logs -l app=flowtodo-backend -c daprd | grep -i "pubsub\|redis"
# Common cause: Redis not ready, component name mismatch
```

### Secrets not loading

```bash
kubectl logs -l app=flowtodo-backend -c flowtodo-backend | grep -i "secret\|dapr"
# Common cause: K8s Secret not created, wrong namespace
kubectl get secret flowtodo-secrets -o yaml
```

### Images not found (ErrImagePull)

```bash
# Ensure images were built inside Minikube's Docker daemon
eval $(minikube docker-env)
docker images | grep hackathon
# If missing, re-run docker build commands
```
