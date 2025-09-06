"""Assist traces integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_REDACTION_LEVEL,
    CONF_SINK_DIR,
    CONF_PARTITIONING,
    DATA_TRACES,
    DATA_WRITER,
    DOMAIN,
    DEFAULT_PARTITIONING,
    DEFAULT_REDACTION,
    DEFAULT_SINK_DIR,
)
from .correlator import Correlator
from .services import async_setup_services
from .websocket import async_setup_ws
from .writer import TraceWriter, WriterConfig


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up assist_traces from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data.setdefault(DATA_TRACES, {})

    sink_dir = entry.options.get(CONF_SINK_DIR, DEFAULT_SINK_DIR)
    partitioning = entry.options.get(CONF_PARTITIONING, DEFAULT_PARTITIONING)
    writer = TraceWriter(WriterConfig(directory=sink_dir, partitioning=partitioning))
    await writer.start()
    hass.data[DATA_WRITER] = writer

    correlator = Correlator(hass)
    hass.data[DOMAIN]["correlator"] = correlator
    hass.data[DOMAIN]["redaction_level"] = entry.options.get(
        CONF_REDACTION_LEVEL, DEFAULT_REDACTION
    )

    await async_setup_services(hass)
    await async_setup_ws(hass)
    hass.config_entries.async_setup_platforms(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload assist_traces config entry."""
    await hass.data[DATA_WRITER].stop()
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True
