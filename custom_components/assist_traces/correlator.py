"""Trace correlator to determine result from HA state changes."""
from __future__ import annotations

import asyncio
from typing import Dict, List

from homeassistant.core import HomeAssistant, callback

from .const import DATA_TRACES


class Correlator:
    """Correlate traces with HA state changes."""

    def __init__(self, hass: HomeAssistant, window: int = 30) -> None:
        self.hass = hass
        self.window = window
        self.pending: Dict[str, Dict[str, List[str]]] = {}
        self._listener = hass.bus.async_listen("state_changed", self._on_state)

    async def add_trace(self, trace_id: str, entity_ids: List[str]) -> None:
        self.pending[trace_id] = {"entities": entity_ids}
        self.hass.loop.create_task(self._timeout(trace_id))

    async def _timeout(self, trace_id: str) -> None:
        await asyncio.sleep(self.window)
        if trace_id in self.pending:
            trace = self.hass.data[DATA_TRACES].get(trace_id)
            if trace:
                trace["result"] = "fail"
            del self.pending[trace_id]

    @callback
    def _on_state(self, event) -> None:
        entity_id = event.data.get("entity_id")
        for trace_id, info in list(self.pending.items()):
            if entity_id in info["entities"]:
                trace = self.hass.data[DATA_TRACES].get(trace_id)
                if trace:
                    trace["result"] = "success"
                del self.pending[trace_id]
