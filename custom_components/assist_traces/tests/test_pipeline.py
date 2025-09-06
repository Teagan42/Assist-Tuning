from __future__ import annotations

import enum
import importlib
import sys
import types
from dataclasses import dataclass

import pytest

from custom_components.assist_traces.const import DATA_TRACES


@pytest.mark.asyncio
async def test_pipeline_from_text_traced(hass):
    """Ensure text pipelines are traced and events stored."""

    class PipelineEventType(enum.Enum):
        RUN_END = "run-end"

    @dataclass
    class PipelineEvent:
        type: PipelineEventType
        data: dict | None = None
        timestamp: str = "2024-06-01T00:00:00"

    async def fake_pipeline(*args, event_callback, **kwargs):
        event_callback(PipelineEvent(PipelineEventType.RUN_END, {"result": "ok"}))
        return "done"

    assist_pipeline = types.SimpleNamespace(
        async_pipeline_from_audio_stream=fake_pipeline,
        async_pipeline_from_text=fake_pipeline,
        PipelineEvent=PipelineEvent,
        PipelineEventType=PipelineEventType,
    )
    components = types.SimpleNamespace(assist_pipeline=assist_pipeline)
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.assist_pipeline"] = assist_pipeline

    # Ensure previous tests don't leave wrapped pipeline functions
    setattr(
        assist_pipeline.async_pipeline_from_audio_stream,
        "_assist_traces_wrapped",
        False,
    )
    setattr(assist_pipeline.async_pipeline_from_text, "_assist_traces_wrapped", False)

    sys.modules.pop("custom_components.assist_traces.pipeline", None)
    pipeline_module = importlib.import_module(
        "custom_components.assist_traces.pipeline"
    )

    hass.data[DATA_TRACES] = {}
    await pipeline_module.async_setup_pipeline_tracing(hass)
    result = await assist_pipeline.async_pipeline_from_text(
        hass, event_callback=lambda e: None
    )

    assert result == "done"
    assert len(hass.data[DATA_TRACES]) == 1
    trace = next(iter(hass.data[DATA_TRACES].values()))
    assert trace["events"][0]["data"] == {"result": "ok"}
    assert trace["events"][0]["type"] == PipelineEventType.RUN_END.value
