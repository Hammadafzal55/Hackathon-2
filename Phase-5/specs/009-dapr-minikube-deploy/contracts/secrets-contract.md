# Contract: Dapr Secrets Store

**Building Block**: Secrets Store
**Component Name**: `kubernetes`
**Backend**: Kubernetes Secrets (native)
**K8s Secret Name**: `flowtodo-secrets`

---

## Secrets Access Pattern

**Client**: `backend/src/services/secrets_loader.py` (new file)
**Called During**: FastAPI application startup (lifespan context manager)
**Dapr Endpoint**: `GET http://localhost:3500/v1.0/secrets/kubernetes/flowtodo-secrets`

### Response Schema

```json
{
  "DATABASE_URL": {"value": "postgresql://..."},
  "BETTER_AUTH_SECRET": {"value": "..."},
  "JWT_SECRET_KEY": {"value": "..."},
  "AI_API_KEY": {"value": "sk-or-v1-..."},
  "redis-password": {"value": ""}
}
```

---

## Secrets Inventory

| Secret Key | Used By | Description |
|------------|---------|-------------|
| `DATABASE_URL` | `database.py` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Frontend env, auth middleware | Better Auth session signing secret |
| `JWT_SECRET_KEY` | `middleware/auth.py` | JWT token verification key |
| `AI_API_KEY` | `services/ai_service.py` | OpenRouter API key |
| `redis-password` | Dapr pubsub/statestore components | Redis auth (empty for local dev) |

---

## Loader Behavior Contract

### Startup Sequence

1. `secrets_loader.load_secrets()` is called in the lifespan startup block.
2. Makes HTTP GET to `http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/kubernetes/flowtodo-secrets`.
3. Extracts each key from the response and calls `os.environ[key] = value`.
4. If Dapr sidecar is unreachable (HTTP connection refused), falls back to existing `os.getenv()` values (local dev without K8s).
5. Logs which mode is active: "Secrets loaded from Dapr" vs "Secrets loaded from environment".

### Fallback Rule

```
if dapr_reachable:
    load from Dapr Secrets API → override os.environ
else:
    use existing os.environ (from K8s pod env or local .env file)
    log warning: "Dapr Secrets Store unavailable — using environment variables"
```

This ensures the backend works both:
- In Minikube with Dapr (reads from Secrets Store)
- Locally without Dapr (reads from .env / environment variables)

---

## Kubernetes Secret Manifest

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: flowtodo-secrets
  namespace: default
type: Opaque
stringData:
  DATABASE_URL: "<postgres-connection-string>"
  BETTER_AUTH_SECRET: "<auth-secret>"
  JWT_SECRET_KEY: "<jwt-secret>"
  AI_API_KEY: "<openrouter-api-key>"
  redis-password: ""
```

This manifest is templated in `todo-chatbot/templates/k8s-secret.yaml` with values sourced from `values.yaml` (secrets section). For security, the `values.yaml` secrets section is documented with placeholder values; actual values are passed via `--set` or a local `values-local.yaml` file that is `.gitignore`d.

---

## Security Notes

- `values.yaml` committed to git must NOT contain real secret values.
- Real secrets passed via `helm upgrade --set secrets.databaseUrl="..."` or via a `values-local.yaml` file.
- The Kubernetes Secret is created/updated by `helm upgrade --install`, never applied manually.
- Dapr Secrets Store uses the in-cluster Kubernetes service account — no additional credentials needed.
