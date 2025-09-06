"""WebSocket API for assist_traces."""

from __future__ import annotations

from typing import Dict

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DATA_TRACES, DOMAIN


async def async_setup_ws(hass: HomeAssistant) -> None:
    """Register WS commands."""

    @websocket_api.websocket_command({"type": f"{DOMAIN}/preview_recent", "limit": int})
    async def preview_recent(hass: HomeAssistant, connection, msg):
        """Return the most recent traces."""
        limit = msg.get("limit", 25)
        traces = list(hass.data[DATA_TRACES].values())[-limit:]
        connection.send_result(msg["id"], traces)

    @websocket_api.websocket_command({"type": f"{DOMAIN}/trace_by_id", "trace_id": str})
    async def trace_by_id(hass: HomeAssistant, connection, msg):
        """Return a single trace by its ID."""
        trace = hass.data[DATA_TRACES].get(msg["trace_id"])  # type: ignore[index]
        connection.send_result(msg["id"], trace)

    @websocket_api.websocket_command({"type": f"{DOMAIN}/stats"})
    async def stats(hass: HomeAssistant, connection, msg):
        """Return statistics about recent traces."""
        traces = list(hass.data[DATA_TRACES].values())
        counts: Dict[str, int] = {}
        latency = []
        for tr in traces:
            counts[tr.get("result", "unknown")] = (
                counts.get(tr.get("result", "unknown"), 0) + 1
            )
            latency.append(tr.get("latency_ms", 0))
        summary = {
            "counts": counts,
            "mean_latency_ms": (sum(latency) / len(latency)) if latency else 0,
        }
        connection.send_result(msg["id"], summary)

    websocket_api.async_register_command(hass, preview_recent)
    websocket_api.async_register_command(hass, trace_by_id)
    websocket_api.async_register_command(hass, stats)
