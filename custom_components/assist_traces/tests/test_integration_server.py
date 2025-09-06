"""Integration tests with a running Home Assistant server."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest
import pytest_asyncio
from homeassistant.core import HomeAssistant

from custom_components.assist_traces import async_setup_entry
from custom_components.assist_traces.const import DATA_TRACES, DOMAIN
from custom_components.assist_traces.tests.conftest import (
    MockConfigEntries,
    MockConfigEntry,
)

# Home Assistant's TTS component depends on the optional ``mutagen`` package.
# Provide a minimal stub so imports succeed without the real dependency.
mutagen_stub = ModuleType("mutagen")
id3_stub = ModuleType("mutagen.id3")


class _ID3:  # pragma: no cover - simple placeholder
    """Dummy ID3 class for tests."""


class _TextFrame:  # pragma: no cover - simple placeholder
    """Dummy TextFrame class for tests."""


id3_stub.ID3 = _ID3
id3_stub.TextFrame = _TextFrame
mutagen_stub.id3 = id3_stub
sys.modules.setdefault("mutagen", mutagen_stub)
sys.modules.setdefault("mutagen.id3", id3_stub)

haffmpeg_stub = ModuleType("haffmpeg")
core_stub = ModuleType("haffmpeg.core")
tools_stub = ModuleType("haffmpeg.tools")


class _HAFFmpeg:  # pragma: no cover - simple placeholder
    """Dummy HAFFmpeg class for tests."""


core_stub.HAFFmpeg = _HAFFmpeg


class _FFVersion:  # pragma: no cover - simple placeholder
    """Dummy FFVersion class for tests."""


class _ImageFrame:  # pragma: no cover - simple placeholder
    """Dummy ImageFrame class for tests."""


tools_stub.IMAGE_JPEG = "jpeg"
tools_stub.FFVersion = _FFVersion
tools_stub.ImageFrame = _ImageFrame
haffmpeg_stub.core = core_stub
haffmpeg_stub.tools = tools_stub
sys.modules.setdefault("haffmpeg", haffmpeg_stub)
sys.modules.setdefault("haffmpeg.core", core_stub)
sys.modules.setdefault("haffmpeg.tools", tools_stub)


@pytest_asyncio.fixture
async def hass_server(event_loop, tmp_path) -> HomeAssistant:
    """Start and yield a running Home Assistant server."""
    hass = HomeAssistant(str(tmp_path))
    hass.loop = event_loop
    hass.config_entries = MockConfigEntries()
    await hass.async_start()
    yield hass
    await hass.async_stop()


@pytest.mark.asyncio
async def test_log_event_records_trace(hass_server: HomeAssistant) -> None:
    """Test that log_event stores traces on a running server."""
    entry = MockConfigEntry(options={})
    await async_setup_entry(hass_server, entry)
    trace = {"trace_id": "abc", "ts": "2024-06-01T00:00:00", "model": "m"}
    await hass_server.services.async_call(
        DOMAIN, "log_event", {"trace": trace}, blocking=True
    )
    assert trace["trace_id"] in hass_server.data[DATA_TRACES]


@pytest.mark.asyncio
async def test_set_feedback_updates_trace(hass_server: HomeAssistant) -> None:
    """Test that set_feedback updates an existing trace."""
    entry = MockConfigEntry(options={})
    await async_setup_entry(hass_server, entry)
    trace = {"trace_id": "abc", "ts": "2024-06-01T00:00:00", "model": "m"}
    await hass_server.services.async_call(
        DOMAIN, "log_event", {"trace": trace}, blocking=True
    )
    await hass_server.services.async_call(
        DOMAIN, "set_feedback", {"trace_id": "abc", "feedback": "up"}, blocking=True
    )
    assert hass_server.data[DATA_TRACES]["abc"]["user_feedback"] == "up"
