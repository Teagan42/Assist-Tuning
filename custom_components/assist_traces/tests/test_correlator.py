from __future__ import annotations

import asyncio
import pytest

from custom_components.assist_traces.const import DATA_TRACES
from custom_components.assist_traces.correlator import Correlator


@pytest.mark.asyncio
async def test_correlator_success(hass):
    hass.data[DATA_TRACES] = {"1": {"trace_id": "1", "ts": "2024-06-01T00:00:00", "model": "m", "result": "unknown"}}
    correlator = Correlator(hass, window=1)
    await correlator.add_trace("1", ["light.kitchen"])
    hass.bus.async_fire("state_changed", {"entity_id": "light.kitchen"})
    await asyncio.sleep(0.1)
    assert hass.data[DATA_TRACES]["1"]["result"] == "success"


@pytest.mark.asyncio
async def test_correlator_fail(hass):
    hass.data[DATA_TRACES] = {"2": {"trace_id": "2", "ts": "2024-06-01T00:00:00", "model": "m", "result": "unknown"}}
    correlator = Correlator(hass, window=0.1)
    await correlator.add_trace("2", ["light.kitchen"])
    await correlator._timeout("2")
    assert hass.data[DATA_TRACES]["2"]["result"] == "fail"
