"""Direct Bedrock client — calls InvokeModel with guardrails.

Supports two auth modes (auto-detected):
  - Bearer token (ABSK key) → Authorization: Bearer header
  - SigV4 (IAM credentials)  → standard AWS signature

Both use the native InvokeModel endpoint and Llama prompt format.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional

import httpx

from app.models import BlockedBy, ChatResponse, ChatMode
from app.signing import (
    build_bearer_headers,
    get_bedrock_endpoint,
    sign_bedrock_request,
    uses_bearer_token,
)

logger = logging.getLogger(__name__)

# Llama prompt format
LLAMA_PROMPT_TEMPLATE = (
    "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
    "{message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
)


def build_invoke_body(message: str) -> dict:
    """Build Bedrock InvokeModel body for Llama."""
    return {
        "prompt": LLAMA_PROMPT_TEMPLATE.format(message=message),
        "max_gen_len": 512,
        "temperature": 0.7,
        "top_p": 0.9,
    }


async def invoke_bedrock_direct(
    message: str,
    model_id: str,
    guardrail_identifier: Optional[str] = None,
    guardrail_version: Optional[str] = None,
) -> ChatResponse:
    """Call Bedrock directly — auto-selects bearer token or SigV4."""
    region = os.environ.get("AWS_REGION", "us-east-1")
    body = build_invoke_body(message)
    url = get_bedrock_endpoint(region, model_id)

    if uses_bearer_token():
        headers = build_bearer_headers(guardrail_identifier, guardrail_version)
        body_bytes = json.dumps(body).encode("utf-8")
    else:
        url, headers, body_bytes = sign_bedrock_request(
            region=region,
            model_id=model_id,
            body=body,
            guardrail_identifier=guardrail_identifier,
            guardrail_version=guardrail_version,
        )

    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, content=body_bytes)

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("Bedrock direct response: status=%d latency=%.1fms", resp.status_code, elapsed_ms)

    # Guardrail intervention — Bedrock returns 400
    if resp.status_code == 400:
        try:
            error_body = resp.json()
            error_msg = error_body.get("message", resp.text)
        except Exception:
            error_msg = resp.text

        return ChatResponse(
            response=f"[BLOCKED by Bedrock Guardrail] {error_msg}",
            mode=ChatMode.DIRECT,
            model=model_id,
            blocked=True,
            blocked_by=BlockedBy.BEDROCK_GUARDRAIL,
            total_latency_ms=elapsed_ms,
        )

    if resp.status_code != 200:
        return ChatResponse(
            response=f"[ERROR] Bedrock returned {resp.status_code}: {resp.text}",
            mode=ChatMode.DIRECT,
            model=model_id,
            total_latency_ms=elapsed_ms,
        )

    resp_json = resp.json()
    generation = resp_json.get("generation", "")

    # Check guardrail intervention header
    guardrail_action = resp.headers.get("x-amzn-bedrock-guardrail-action")
    if guardrail_action == "INTERVENED":
        return ChatResponse(
            response=f"[BLOCKED by Bedrock Guardrail] {generation}",
            mode=ChatMode.DIRECT,
            model=model_id,
            blocked=True,
            blocked_by=BlockedBy.BEDROCK_GUARDRAIL,
            total_latency_ms=elapsed_ms,
        )

    return ChatResponse(
        response=generation,
        mode=ChatMode.DIRECT,
        model=model_id,
        blocked=False,
        blocked_by=BlockedBy.NONE,
        total_latency_ms=elapsed_ms,
    )
