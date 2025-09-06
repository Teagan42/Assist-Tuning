"""Tests for integration setup and teardown."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass

import pytest


@pytest.mark.asyncio
async def test_setup_and_unload_entry(hass, tmp_path):
    """Initialize and unload the integration entry."""
    calls = {}

    async def dummy_pipeline(hass):
        calls["pipeline"] = True

    async def dummy_services(hass):
        calls["services"] = True

    async def dummy_ws(hass):
        calls["ws"] = True

    @dataclass
    class DummyConfig:
        directory: str
        partitioning: str = "daily"

    class DummyWriter:
        def __init__(self, config):
            self.started = False
            self.stopped = False

        async def start(self):
            self.started = True

        async def stop(self):
            self.stopped = True

        async def enqueue(self, trace):  # pragma: no cover - not used
            pass

    sys_modules = {
        "custom_components.assist_traces.pipeline": types.SimpleNamespace(
            async_setup_pipeline_tracing=dummy_pipeline
        ),
        "custom_components.assist_traces.services": types.SimpleNamespace(
            async_setup_services=dummy_services
        ),
        "custom_components.assist_traces.websocket": types.SimpleNamespace(
            async_setup_ws=dummy_ws
        ),
        "custom_components.assist_traces.writer": types.SimpleNamespace(
            TraceWriter=DummyWriter, WriterConfig=DummyConfig
        ),
        "custom_components.assist_traces.correlator": types.SimpleNamespace(
            Correlator=lambda hass: object()
        ),
    }
    orig_modules = {}
    for name, module in sys_modules.items():
        orig_modules[name] = sys.modules.get(name)
        sys.modules[name] = module

    try:
        from custom_components.assist_traces import (
            async_setup_entry,
            async_unload_entry,
        )

        entry = types.SimpleNamespace(options={})
        assert await async_setup_entry(hass, entry)
        assert calls == {"pipeline": True, "services": True, "ws": True}

        writer = hass.data.get("writer")
        assert isinstance(writer, DummyWriter)

        assert await async_unload_entry(hass, entry)
        assert writer.stopped is True
    finally:
        for name, module in orig_modules.items():
            if module is None:
                del sys.modules[name]
            else:
                sys.modules[name] = module
