"""Tests for pipeline tracing wrappers."""

from __future__ import annotations

import asyncio
import sys
import types
from enum import Enum

import pytest

from custom_components.assist_traces.const import DATA_TRACES, DATA_WRITER


class DummyWriter:
    """Collect traces enqueued by the pipeline."""

    def __init__(self) -> None:
        self.traces = []

    async def enqueue(self, trace):
        self.traces.append(trace)


class PipelineEventType(Enum):
    """Minimal pipeline event types."""

    RUN_END = "run-end"


class PipelineEvent:
    """Simplified pipeline event object."""

    def __init__(self, type, data=None, timestamp=0):
        self.type = type
        self.data = data or {}
        self.timestamp = timestamp


async def _audio(*args, event_callback, **kwargs):
    event_callback(PipelineEvent(PipelineEventType.RUN_END, {}, 1))
    return "audio"


async def _text(*args, event_callback, **kwargs):
    event_callback(PipelineEvent(PipelineEventType.RUN_END, {}, 1))
    return "text"


@pytest.mark.asyncio
async def test_traces_audio_and_text(hass):
    """Wrap audio and text pipelines and capture traces."""
    mod = types.SimpleNamespace(
        async_pipeline_from_audio_stream=_audio,
        async_pipeline_from_text=_text,
        PipelineEvent=PipelineEvent,
        PipelineEventType=PipelineEventType,
    )
    sys.modules["homeassistant.components.assist_pipeline"] = mod

    from custom_components.assist_traces.pipeline import async_setup_pipeline_tracing

    hass.data[DATA_TRACES] = {}
    hass.data[DATA_WRITER] = DummyWriter()
    await async_setup_pipeline_tracing(hass)

    await mod.async_pipeline_from_audio_stream(hass, event_callback=lambda e: None)
    await mod.async_pipeline_from_text(hass, "hi", event_callback=lambda e: None)
    await asyncio.sleep(0)
    pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    if pending:
        await asyncio.gather(*pending)

    assert len(hass.data[DATA_TRACES]) == 2
