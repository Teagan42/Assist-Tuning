"""Integration tests with a running Home Assistant server."""

from __future__ import annotations

import pytest
import pytest_asyncio
from homeassistant.core import HomeAssistant

from custom_components.assist_traces import async_setup_entry
from custom_components.assist_traces.const import DATA_TRACES, DOMAIN
from custom_components.assist_traces.tests.conftest import (
    MockConfigEntries,
    MockConfigEntry,
)


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
