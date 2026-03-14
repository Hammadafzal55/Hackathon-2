"""
Dapr Service Invocation demonstration endpoint.
Calls the backend itself through the Dapr sidecar to prove mTLS and distributed
tracing (Zipkin) are working.
"""
import logging
import os
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException

from src.middleware.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
DAPR_APP_ID = os.getenv("DAPR_APP_ID", "flowtodo-backend")


@router.get("/dapr/self-invoke-test")
async def dapr_self_invoke_test(
    current_user_id: UUID = Depends(get_current_user_id),
) -> dict:
    """
    Demonstrates Dapr Service Invocation with mTLS.

    Calls GET /health on this same service via the Dapr sidecar at
    http://localhost:3500/v1.0/invoke/flowtodo-backend/method/health

    This generates a 2-span distributed trace visible in Zipkin.
    """
    dapr_url = (
        f"http://localhost:{DAPR_HTTP_PORT}"
        f"/v1.0/invoke/{DAPR_APP_ID}/method/health"
    )

    logger.info(
        f"Service invocation test: calling {dapr_url} "
        f"(user={current_user_id})"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(dapr_url)
            response.raise_for_status()
            invocation_result = response.json()

        logger.info(
            f"Service invocation succeeded via Dapr sidecar "
            f"(app-id={DAPR_APP_ID})"
        )

        return {
            "status": "ok",
            "message": "Dapr Service Invocation with mTLS succeeded",
            "dapr_app_id": DAPR_APP_ID,
            "invocation_result": invocation_result,
            "hint": "Check Zipkin at http://localhost:9411 for the distributed trace",
        }

    except httpx.ConnectError:
        logger.warning(
            "Dapr sidecar not available — running outside Kubernetes?"
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "Dapr sidecar unavailable. "
                "This endpoint requires deployment to Minikube with Dapr."
            ),
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Dapr invocation returned {e.response.status_code}")
        raise HTTPException(
            status_code=502,
            detail=f"Dapr invocation failed with status {e.response.status_code}",
        )
