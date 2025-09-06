import types
import pytest

from custom_components.assist_traces.const import DATA_TRACES
from custom_components.assist_traces.pipeline import setup_pipeline_tracing


@pytest.mark.asyncio
async def test_pipeline_tracing(hass):
    import hassil.recognize as hassil_recognize
    hassil_recognize.UnmatchedRangeEntity = type(
        "UnmatchedRangeEntity", (), {}
    )

    try:
        from homeassistant.components.assist_pipeline.pipeline import (
            KEY_ASSIST_PIPELINE,
            PipelineEvent,
            PipelineEventType,
            PipelineRun,
        )
    except ImportError:
        pytest.skip("assist_pipeline dependencies not available")

    setup_pipeline_tracing(hass)

    class DummyRunDebug:
        def __init__(self):
            self.events = []

    class DummyPipeline:
        id = "pipe"

    class DummyPipelineData:
        def __init__(self):
            self.pipeline_debug = {"pipe": {"run1": DummyRunDebug()}}

    hass.data[KEY_ASSIST_PIPELINE] = DummyPipelineData()

    run = types.SimpleNamespace(
        id="run1",
        hass=hass,
        pipeline=DummyPipeline(),
        event_callback=lambda e: None,
    )

    PipelineRun.process_event(run, PipelineEvent(PipelineEventType.RUN_START, {}))

    assert "run1" in hass.data[DATA_TRACES]
    trace = hass.data[DATA_TRACES]["run1"]
    assert trace["trace_id"] == "run1"
    assert trace["ha_events"][0]["type"] == PipelineEventType.RUN_START
