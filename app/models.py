"""Pydantic models for the EthicalZen AWS Accelerator demo."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChatMode(str, Enum):
    DIRECT = "direct"
    MODE_A = "mode-a"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt")
    mode: ChatMode = Field(ChatMode.MODE_A, description="Routing mode: 'direct' or 'mode-a'")
    model_id: str = Field(
        "meta.llama3-8b-instruct-v1:0",
        description="Bedrock model ID",
    )
    guardrail_identifier: Optional[str] = Field(None, description="Bedrock guardrail ID")
    guardrail_version: Optional[str] = Field(None, description="Bedrock guardrail version")


class BlockedBy(str, Enum):
    NONE = "none"
    BEDROCK_GUARDRAIL = "bedrock_guardrail"
    ETHICALZEN_GUARDRAIL = "ethicalzen_guardrail"


class ChatResponse(BaseModel):
    response: str
    mode: ChatMode
    model: str
    blocked: bool = False
    blocked_by: BlockedBy = BlockedBy.NONE
    trace_id: Optional[str] = None
    ethicalzen_status: Optional[str] = None
    validation_ms: Optional[float] = None
    total_latency_ms: float = 0.0


class EventLog(BaseModel):
    """Structured event log written to logs/events.jsonl."""
    trace_id: Optional[str] = None
    mode: str = ""
    model: str = ""
    guardrail_identifier: Optional[str] = None
    guardrail_version: Optional[str] = None
    ethicalzen_status: Optional[str] = None
    blocked: bool = False
    blocked_by: str = "none"
    validation_ms: Optional[float] = None
    total_latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BedrockPayload(BaseModel):
    """Bedrock Llama InvokeModel request body."""
    prompt: str
    max_gen_len: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
