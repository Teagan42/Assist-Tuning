"""Telemetry sensors for assist_traces."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, List

from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant

from .const import DATA_TRACES


class AssistTracesSensor(Entity):
    def __init__(self, hass: HomeAssistant, name: str, func: Callable[[], float]) -> None:
        self._hass = hass
        self._attr_name = name
        self._func = func

    @property
    def state(self):
        return self._func()


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    def recent_traces() -> List[dict]:
        traces = list(hass.data.get(DATA_TRACES, {}).values())
        cutoff = datetime.utcnow() - timedelta(hours=24)
        return [t for t in traces if datetime.fromisoformat(t["ts"]) >= cutoff]

    async_add_entities(
        [
            AssistTracesSensor(hass, "assist_traces_count_24h", lambda: len(recent_traces())),
            AssistTracesSensor(
                hass,
                "assist_traces_fail_rate_24h",
                lambda: sum(1 for t in recent_traces() if t.get("result") == "fail") / max(len(recent_traces()), 1),
            ),
            AssistTracesSensor(
                hass,
                "assist_traces_mean_latency_ms",
                lambda: sum(t.get("latency_ms", 0) for t in recent_traces()) / max(len(recent_traces()), 1),
            ),
        ]
    )
