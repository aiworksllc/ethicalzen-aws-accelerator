"""Structured event logging — writes JSON-lines to logs/events.jsonl."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from app.models import ChatResponse, EventLog

logger = logging.getLogger(__name__)

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
EVENTS_FILE = LOGS_DIR / "events.jsonl"


def setup_logging() -> None:
    """Configure structured console logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def log_event(
    response: ChatResponse,
    guardrail_identifier: str | None = None,
    guardrail_version: str | None = None,
) -> EventLog:
    """Persist a structured event to logs/events.jsonl and return it."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    event = EventLog(
        trace_id=response.trace_id,
        mode=response.mode.value,
        model=response.model,
        guardrail_identifier=guardrail_identifier,
        guardrail_version=guardrail_version,
        ethicalzen_status=response.ethicalzen_status,
        blocked=response.blocked,
        blocked_by=response.blocked_by.value if hasattr(response.blocked_by, "value") else str(response.blocked_by),
        validation_ms=response.validation_ms,
        total_latency_ms=response.total_latency_ms,
    )

    with open(EVENTS_FILE, "a") as f:
        f.write(event.model_dump_json() + "\n")

    logger.info("Event logged: trace=%s blocked=%s blocked_by=%s", event.trace_id, event.blocked, event.blocked_by)
    return event
