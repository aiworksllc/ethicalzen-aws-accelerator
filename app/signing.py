"""AWS auth for Bedrock runtime requests.

Supports two auth modes:
  1. Bearer token (ABSK key) — Authorization: Bearer <token>
  2. SigV4 signing (IAM credentials) — standard AWS signature

Both use the native InvokeModel endpoint:
  https://bedrock-runtime.{region}.amazonaws.com/model/{modelId}/invoke

The mode is auto-detected: if AWS_BEARER_TOKEN_BEDROCK is set, bearer mode
is used.  Otherwise falls back to SigV4 with AWS_ACCESS_KEY_ID/SECRET.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional


def uses_bearer_token() -> bool:
    """Return True if a Bedrock bearer token is configured."""
    return bool(os.environ.get("AWS_BEARER_TOKEN_BEDROCK"))


def get_bedrock_endpoint(region: str, model_id: str) -> str:
    """Return the Bedrock InvokeModel URL."""
    return (
        f"https://bedrock-runtime.{region}.amazonaws.com"
        f"/model/{model_id}/invoke"
    )


def build_bearer_headers(
    guardrail_identifier: Optional[str] = None,
    guardrail_version: Optional[str] = None,
) -> dict[str, str]:
    """Build headers for bearer-token auth."""
    token = os.environ["AWS_BEARER_TOKEN_BEDROCK"]
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if guardrail_identifier:
        headers["X-Amzn-Bedrock-GuardrailIdentifier"] = guardrail_identifier
    if guardrail_version:
        headers["X-Amzn-Bedrock-GuardrailVersion"] = guardrail_version
    return headers


def sign_bedrock_request(
    region: str,
    model_id: str,
    body: dict[str, Any],
    guardrail_identifier: Optional[str] = None,
    guardrail_version: Optional[str] = None,
) -> tuple[str, dict[str, str], bytes]:
    """Sign a Bedrock InvokeModel request with SigV4.

    Returns:
        (url, signed_headers, body_bytes)
    """
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials

    access_key = os.environ["AWS_ACCESS_KEY_ID"]
    secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    session_token = os.environ.get("AWS_SESSION_TOKEN")
    credentials = Credentials(access_key, secret_key, session_token)

    url = get_bedrock_endpoint(region, model_id)
    body_bytes = json.dumps(body).encode("utf-8")

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if guardrail_identifier:
        headers["X-Amzn-Bedrock-GuardrailIdentifier"] = guardrail_identifier
    if guardrail_version:
        headers["X-Amzn-Bedrock-GuardrailVersion"] = guardrail_version

    aws_request = AWSRequest(method="POST", url=url, data=body_bytes, headers=headers)
    SigV4Auth(credentials, "bedrock", region).add_auth(aws_request)

    signed_headers = dict(aws_request.headers)
    return url, signed_headers, body_bytes
