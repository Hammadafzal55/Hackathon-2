"""
Dapr Secrets Store loader.
Loads application secrets from the Dapr Kubernetes Secrets Store at startup.
Falls back to environment variables when Dapr sidecar is unavailable (local dev).
"""
import os
import logging

import httpx

logger = logging.getLogger(__name__)

# Keys to load from the Dapr Secrets Store
SECRET_KEYS = [
    "DATABASE_URL",
    "BETTER_AUTH_SECRET",
    "JWT_SECRET_KEY",
    "AI_API_KEY",
]

DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
SECRET_STORE_NAME = "kubernetes"
SECRET_NAME = "flowtodo-secrets"


async def load_secrets() -> None:
    """
    Fetch secrets from the Dapr Kubernetes Secrets Store and inject them
    into os.environ so downstream code (database.py, auth middleware) picks
    them up without any changes.

    Gracefully falls back to existing os.environ values if Dapr is unreachable.
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/{SECRET_STORE_NAME}/{SECRET_NAME}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        loaded = []
        for key in SECRET_KEYS:
            if key in data and data[key].get("value"):
                os.environ[key] = data[key]["value"]
                loaded.append(key)

        logger.info(f"Secrets loaded from Dapr Secrets Store: {loaded}")

    except (httpx.ConnectError, httpx.ConnectTimeout):
        logger.warning(
            "Dapr Secrets Store unavailable — using environment variables. "
            "(Expected when running outside Kubernetes)"
        )
    except httpx.HTTPStatusError as e:
        logger.warning(
            f"Dapr Secrets Store returned {e.response.status_code} — "
            f"using environment variables. URL: {url}"
        )
    except Exception as e:
        logger.warning(
            f"Failed to load secrets from Dapr ({type(e).__name__}: {e}) — "
            "using environment variables."
        )
