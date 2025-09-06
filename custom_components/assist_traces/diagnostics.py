"""Diagnostics for assist_traces."""
from __future__ import annotations

from typing import Any, Dict

from homeassistant.core import HomeAssistant

from .const import DATA_WRITER


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry) -> Dict[str, Any]:
    """Return diagnostics for a config entry."""
    writer = hass.data.get(DATA_WRITER)
    return {"options": entry.options, "queue_size": writer.queue.qsize() if writer else 0}
