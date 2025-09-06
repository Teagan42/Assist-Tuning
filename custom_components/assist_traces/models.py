"""Data models for assist_traces."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

ResultType = Literal["unknown", "success", "partial", "fail"]


class TruncationInfo(BaseModel):
    """Information about prompt truncation."""

    was_truncated: bool = False
    prompt_tokens_before: int = 0
    prompt_tokens_after: int = 0


class ToolCall(BaseModel):
    """Tool call representation."""

    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    response: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None
    error: Optional[str] = None


class AssistTrace(BaseModel):
    """Full trace of an assist pipeline request."""

    trace_id: str
    ts: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    user_text: Optional[str] = None
    audio_sha256: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    entities: Dict[str, Any] = Field(default_factory=dict)

    prompt_template_id: Optional[str] = ""
    prompt_rendered: str = ""
    truncation: TruncationInfo = Field(default_factory=TruncationInfo)

    model: str = ""
    params: Dict[str, Any] = Field(default_factory=dict)
    response_text: str = ""
    tool_calls: List[ToolCall] = Field(default_factory=list)
    parsed_action: Optional[Dict[str, Any]] = None
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    result: ResultType = "unknown"
    ha_events: List[Dict[str, Any]] = Field(default_factory=list)
    user_feedback: Optional[str] = None
    repair_text: Optional[str] = None
    gold_action: Optional[Dict[str, Any]] = None
