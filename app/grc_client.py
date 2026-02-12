"""GRC client — fetches OSCAL assessment results from EthicalZen portal.

The portal already generates OSCAL 1.1.2 Assessment Results from
evidence logs captured by the gateway.  This client simply fetches them.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

PORTAL_BASE = "https://api.ethicalzen.ai"


async def fetch_oscal_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    framework: Optional[str] = None,
) -> dict:
    """Fetch OSCAL Assessment Results from the EthicalZen portal.

    Args:
        start_time: ISO 8601 start filter (optional)
        end_time:   ISO 8601 end filter (optional)
        framework:  nist_ai_rmf | iso_42001 | nist_csf (optional)

    Returns:
        Raw JSON response including the OSCAL document.
    """
    api_key = os.environ["ETHICALZEN_API_KEY"]
    tenant_id = os.environ.get("ETHICALZEN_TENANT_ID", "demo")

    headers = {
        "X-API-Key": api_key,
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json",
    }

    body: dict = {}
    if start_time:
        body["startTime"] = start_time
    if end_time:
        body["endTime"] = end_time
    if framework:
        body["framework"] = framework

    url = f"{PORTAL_BASE}/api/v2/grc/export/oscal"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=body)

    logger.info("OSCAL export: status=%d events=%s", resp.status_code, resp.json().get("eventCount"))
    return resp.json()


async def fetch_stix_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """Fetch STIX 2.1 Bundle from the EthicalZen portal."""
    api_key = os.environ["ETHICALZEN_API_KEY"]
    tenant_id = os.environ.get("ETHICALZEN_TENANT_ID", "demo")

    headers = {
        "X-API-Key": api_key,
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json",
    }

    body: dict = {}
    if start_time:
        body["startTime"] = start_time
    if end_time:
        body["endTime"] = end_time

    url = f"{PORTAL_BASE}/api/v2/grc/export/stix"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=body)

    return resp.json()
