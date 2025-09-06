"""Assist pipeline event tracing."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from homeassistant.core import HomeAssistant

from .const import DATA_TRACES, DATA_WRITER


def setup_pipeline_tracing(hass: HomeAssistant) -> None:
    """Patch PipelineRun.process_event to collect pipeline events."""
    from homeassistant.components.assist_pipeline.pipeline import (
        PipelineEvent,
        PipelineEventType,
        PipelineRun,
    )

    if getattr(PipelineRun, "_assist_traces_patched", False):
        return

    original = PipelineRun.process_event

    def _process_event(self: PipelineRun, event: PipelineEvent) -> None:
        traces = hass.data.setdefault(DATA_TRACES, {})
        trace = traces.setdefault(
            self.id,
            {"trace_id": self.id, "ts": event.timestamp, "ha_events": []},
        )

        trace["ha_events"].append(asdict(event))

        if event.type == PipelineEventType.STT_END and event.data:
            trace["user_text"] = event.data.get("stt_output", {}).get("text")

        if event.type == PipelineEventType.INTENT_END and event.data:
            intent_output = event.data.get("intent_output", {})
            response = intent_output.get("response") or {}
            speech = response.get("speech", {})
            plain = speech.get("plain", {})
            trace["response_text"] = plain.get("text")
            trace["context"] = intent_output.get("context", {})
            trace["entities"] = intent_output.get("entities", {})

        if event.type == PipelineEventType.RUN_END:
            try:
                start_ts = datetime.fromisoformat(trace["ts"])
                end_ts = datetime.fromisoformat(event.timestamp)
                trace["latency_ms"] = int(
                    (end_ts - start_ts).total_seconds() * 1000
                )
            except Exception:
                pass
            writer = hass.data.get(DATA_WRITER)
            if writer:
                hass.loop.create_task(writer.enqueue(dict(trace)))

        original(self, event)

    PipelineRun.process_event = _process_event  # type: ignore[assignment]
    PipelineRun._assist_traces_patched = True
