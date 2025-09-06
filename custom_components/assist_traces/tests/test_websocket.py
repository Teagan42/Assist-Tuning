from __future__ import annotations

import pytest
import sys
import types

# Stub hass_nabucasa to avoid heavy deps
sys.modules.setdefault("hass_nabucasa", types.ModuleType("hass_nabucasa"))
sys.modules.setdefault("hass_nabucasa.remote", types.ModuleType("remote"))

from homeassistant.components import websocket_api

from custom_components.assist_traces.const import DATA_TRACES, DOMAIN
from custom_components.assist_traces.websocket import async_setup_ws


class DummyConnection:
    def __init__(self):
        self.result = None

    def send_result(self, msg_id, result):
        self.result = result

    def send_error(self, *args, **kwargs):
        self.result = {"error": args}


@pytest.mark.asyncio
async def test_preview_recent(hass):
    await async_setup_ws(hass)
    hass.data[DATA_TRACES] = {
        "1": {"trace_id": "1", "ts": "2024-06-01T00:00:00", "model": "m"}
    }
    handler = hass.data["websocket_api"][f"{DOMAIN}/preview_recent"][0]
    conn = DummyConnection()
    await handler(hass, conn, {"id": 1, "type": f"{DOMAIN}/preview_recent", "limit": 1})
    assert conn.result[0]["trace_id"] == "1"
