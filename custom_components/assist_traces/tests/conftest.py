"""Pytest fixtures."""

from __future__ import annotations

import pytest
import sys
import types

from homeassistant.core import HomeAssistant
import pytest_asyncio

# Stub hass_nabucasa to avoid heavy dependencies
sys.modules.setdefault("hass_nabucasa", types.ModuleType("hass_nabucasa"))
sys.modules.setdefault("hass_nabucasa.remote", types.ModuleType("remote"))
sys.modules.setdefault("hass_nabucasa.acme", types.ModuleType("acme"))


@pytest.fixture
def event_loop():
    """Provide an isolated event loop for each test."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


class MockConfigEntries:
    """Minimal stand-in for Home Assistant's config entries manager."""

    async def async_setup_platforms(self, entry, platforms):
        """Pretend to set up platforms for the given entry."""
        return True

    async def async_unload_platforms(self, entry, platforms):
        """Pretend to unload platforms for the given entry."""
        return True


class MockConfigEntry:
    """Simple container for config entry options used in tests."""

    def __init__(self, options=None):
        """Initialize the config entry with optional settings."""
        self.options = options or {}


@pytest_asyncio.fixture
async def hass(event_loop, tmp_path) -> HomeAssistant:
    """Return a Home Assistant instance for testing."""
    hass = HomeAssistant(str(tmp_path))
    hass.loop = event_loop
    hass.config_entries = MockConfigEntries()
    return hass
