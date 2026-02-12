"""EthicalZen proxy client — Mode A (Complement Mode).

Routes the Bedrock request through the EthicalZen ACVPS Gateway at /api/proxy.
The gateway performs prompt injection detection and additional guardrail
evaluation before forwarding to Bedrock.

Both bearer-token and SigV4 auth use the native InvokeModel endpoint.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional

import httpx

from app.models import BlockedBy, ChatResponse, ChatMode
from app.bedrock_client import build_invoke_body
from app.signing import (
    build_bearer_headers,
    get_bedrock_endpoint,
    sign_bedrock_request,
    uses_bearer_token,
)

logger = logging.getLogger(__name__)


def _get_proxy_url() -> str:
    """Return the EthicalZen proxy base URL."""
    base = os.environ.get("ETHICALZEN_PROXY_URL", "https://gateway.ethicalzen.ai")
    return f"{base.rstrip('/')}/api/proxy"


async def invoke_via_proxy(
    message: str,
    model_id: str,
    guardrail_identifier: Optional[str] = None,
    guardrail_version: Optional[str] = None,
) -> ChatResponse:
    """Send a Bedrock request through the EthicalZen proxy (Mode A).

    Flow:
        App  →  EthicalZen Proxy (/api/proxy)
             →  Bedrock Runtime (InvokeModel) with guardrails
             →  Response  →  EthicalZen post-validation  →  App
    """
    region = os.environ.get("AWS_REGION", "us-east-1")
    api_key = os.environ["ETHICALZEN_API_KEY"]
    dc_id = os.environ["ETHICALZEN_DC_ID"]
    dc_digest = os.environ.get("ETHICALZEN_DC_DIGEST", "")
    dc_suite = os.environ.get("ETHICALZEN_DC_SUITE", "bedrock-guardrail-complement")
    tenant_id = os.environ.get("ETHICALZEN_TENANT_ID", "default")

    body = build_invoke_body(message)
    target_url = get_bedrock_endpoint(region, model_id)

    # Build auth headers based on available credentials
    if uses_bearer_token():
        auth_headers = build_bearer_headers(guardrail_identifier, guardrail_version)
        body_bytes = json.dumps(body).encode("utf-8")
    else:
        _, auth_headers, body_bytes = sign_bedrock_request(
            region=region,
            model_id=model_id,
            body=body,
            guardrail_identifier=guardrail_identifier,
            guardrail_version=guardrail_version,
        )

    # Build proxy headers — EthicalZen gateway needs these to route and validate
    proxy_headers: dict[str, str] = {
        "X-API-Key": api_key,
        "X-DC-Id": dc_id,
        "X-DC-Digest": dc_digest,
        "X-DC-Suite": dc_suite,
        "X-Target-Endpoint": target_url,
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json",
    }

    # Forward auth and Bedrock-specific headers
    forward_keys = (
        "Authorization", "X-Amz-Date", "X-Amz-Security-Token",
        "X-Amz-Content-Sha256", "X-Amzn-Bedrock-GuardrailIdentifier",
        "X-Amzn-Bedrock-GuardrailVersion",
    )
    for key in forward_keys:
        if key in auth_headers:
            proxy_headers[key] = auth_headers[key]

    proxy_url = _get_proxy_url()
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(proxy_url, headers=proxy_headers, content=body_bytes)

    elapsed_ms = (time.perf_counter() - start) * 1000

    # Read EthicalZen response headers
    acvps_status = resp.headers.get("X-ACVPS-Status")
    trace_id = resp.headers.get("X-ACVPS-Trace-ID")
    validation_ms_raw = resp.headers.get("X-ACVPS-Validation-Ms")
    validation_ms = float(validation_ms_raw) if validation_ms_raw else None

    logger.info(
        "Proxy response: status=%d acvps_status=%s trace=%s validation=%.1fms latency=%.1fms",
        resp.status_code,
        acvps_status,
        trace_id,
        validation_ms or 0,
        elapsed_ms,
    )

    # EthicalZen blocked the request (prompt injection, policy violation, etc.)
    if acvps_status and acvps_status.upper() in ("BLOCKED", "REJECTED", "DENIED"):
        try:
            error_body = resp.json()
            error_msg = error_body.get("error", error_body.get("message", resp.text))
        except Exception:
            error_msg = resp.text

        return ChatResponse(
            response=f"[BLOCKED by EthicalZen] {error_msg}",
            mode=ChatMode.MODE_A,
            model=model_id,
            blocked=True,
            blocked_by=BlockedBy.ETHICALZEN_GUARDRAIL,
            trace_id=trace_id,
            ethicalzen_status=acvps_status,
            validation_ms=validation_ms,
            total_latency_ms=elapsed_ms,
        )

    # Bedrock guardrail blocked the request (forwarded through proxy)
    if resp.status_code == 400:
        try:
            error_body = resp.json()
            error_msg = error_body.get("message", resp.text)
        except Exception:
            error_msg = resp.text

        return ChatResponse(
            response=f"[BLOCKED by Bedrock Guardrail] {error_msg}",
            mode=ChatMode.MODE_A,
            model=model_id,
            blocked=True,
            blocked_by=BlockedBy.BEDROCK_GUARDRAIL,
            trace_id=trace_id,
            ethicalzen_status=acvps_status,
            validation_ms=validation_ms,
            total_latency_ms=elapsed_ms,
        )

    if resp.status_code != 200:
        return ChatResponse(
            response=f"[ERROR] Proxy returned {resp.status_code}: {resp.text}",
            mode=ChatMode.MODE_A,
            model=model_id,
            trace_id=trace_id,
            ethicalzen_status=acvps_status,
            validation_ms=validation_ms,
            total_latency_ms=elapsed_ms,
        )

    resp_json = resp.json()
    generation = resp_json.get("generation", "")

    # Check if Bedrock guardrail intervened in the response
    guardrail_action = resp.headers.get("x-amzn-bedrock-guardrail-action")
    if guardrail_action == "INTERVENED":
        return ChatResponse(
            response=f"[BLOCKED by Bedrock Guardrail] {generation}",
            mode=ChatMode.MODE_A,
            model=model_id,
            blocked=True,
            blocked_by=BlockedBy.BEDROCK_GUARDRAIL,
            trace_id=trace_id,
            ethicalzen_status=acvps_status,
            validation_ms=validation_ms,
            total_latency_ms=elapsed_ms,
        )

    return ChatResponse(
        response=generation,
        mode=ChatMode.MODE_A,
        model=model_id,
        blocked=False,
        blocked_by=BlockedBy.NONE,
        trace_id=trace_id,
        ethicalzen_status=acvps_status,
        validation_ms=validation_ms,
        total_latency_ms=elapsed_ms,
    )
