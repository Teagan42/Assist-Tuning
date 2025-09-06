"""Assist pipeline tracing hooks."""

from __future__ import annotations

import uuid
from typing import Any, Dict

from homeassistant.components import assist_pipeline
from homeassistant.core import HomeAssistant

from .const import DATA_TRACES, DATA_WRITER


async def async_setup_pipeline_tracing(hass: HomeAssistant) -> None:
    """Wrap Assist pipelines to capture events for tracing."""
    if getattr(
        assist_pipeline.async_pipeline_from_audio_stream,
        "_assist_traces_wrapped",
        False,
    ):
        return

    def _wrap(original):
        """Wrap an Assist pipeline function to capture events."""

        async def traced(*args, event_callback, **kwargs):
            """Capture pipeline events while delegating to the original implementation."""
            trace: Dict[str, Any] = {"events": []}
            trace_id = uuid.uuid4().hex

            def _capture(event: assist_pipeline.PipelineEvent) -> None:
                """Store each pipeline event and dispatch to the original callback."""
                trace.setdefault("ts", event.timestamp)
                trace["events"].append(
                    {
                        "type": event.type.value,
                        "data": event.data,
                        "timestamp": event.timestamp,
                    }
                )
                event_callback(event)
                if event.type == assist_pipeline.PipelineEventType.RUN_END:
                    trace["trace_id"] = trace_id
                    trace.setdefault("model", "assist-pipeline")
                    hass.data[DATA_TRACES][trace_id] = trace
                    writer = hass.data.get(DATA_WRITER)
                    if writer is not None:
                        hass.async_create_task(writer.enqueue(trace))

            return await original(*args, event_callback=_capture, **kwargs)

        traced._assist_traces_wrapped = True
        return traced

    assist_pipeline.async_pipeline_from_audio_stream = _wrap(
        assist_pipeline.async_pipeline_from_audio_stream
    )
    if hasattr(assist_pipeline, "async_pipeline_from_text"):
        assist_pipeline.async_pipeline_from_text = _wrap(
            assist_pipeline.async_pipeline_from_text
        )
