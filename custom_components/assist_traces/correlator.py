"""Trace correlator to determine result from HA state changes."""
from __future__ import annotations

import asyncio
from typing import Dict, List

from homeassistant.core import HomeAssistant, callback

from .const import DATA_TRACES


class Correlator:
    """Correlate traces with HA state changes."""

    def __init__(self, hass: HomeAssistant, window: int = 30) -> None:
        """Initialize the correlator."""
        self.hass = hass
        self.window = window
        self.pending: Dict[str, Dict[str, List[str]]] = {}
        self._listener = hass.bus.async_listen("state_changed", self._on_state)

    async def add_trace(self, trace_id: str, entity_ids: List[str]) -> None:
        """Register a trace to watch for state changes."""
        self.pending[trace_id] = {"entities": entity_ids}
        self.hass.loop.create_task(self._timeout(trace_id))

    async def _timeout(self, trace_id: str) -> None:
        """Mark a trace as failed if no matching state change occurs."""
        await asyncio.sleep(self.window)
        if trace_id in self.pending:
            trace = self.hass.data[DATA_TRACES].get(trace_id)
            if trace:
                trace["result"] = "fail"
            del self.pending[trace_id]

    @callback
    def _on_state(self, event) -> None:
        """Handle state change events and mark traces as successful."""
        entity_id = event.data.get("entity_id")
        for trace_id, info in list(self.pending.items()):
            if entity_id in info["entities"]:
                trace = self.hass.data[DATA_TRACES].get(trace_id)
                if trace:
                    trace["result"] = "success"
                del self.pending[trace_id]
