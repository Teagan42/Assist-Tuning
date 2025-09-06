"""Pytest fixtures."""

from __future__ import annotations

import pytest
import sys
import types

import pytest_asyncio
from homeassistant.core import HomeAssistant
import hassil.recognize as hassil_recognize

# Stub hass_nabucasa to avoid heavy dependencies
sys.modules.setdefault("hass_nabucasa", types.ModuleType("hass_nabucasa"))
sys.modules.setdefault("hass_nabucasa.remote", types.ModuleType("remote"))
sys.modules.setdefault("hass_nabucasa.acme", types.ModuleType("acme"))
home_intents = types.ModuleType("home_assistant_intents")
home_intents.ErrorKey = Exception
home_intents.get_intents = lambda: {}
home_intents.get_languages = lambda: []
sys.modules.setdefault("home_assistant_intents", home_intents)
setattr(hassil_recognize, "UnmatchedRangeEntity", type("UnmatchedRangeEntity", (), {}))


@pytest.fixture
def event_loop():
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


class MockConfigEntries:
    async def async_setup_platforms(self, entry, platforms):
        return True

    async def async_unload_platforms(self, entry, platforms):
        return True


class MockConfigEntry:
    def __init__(self, options=None):
        self.options = options or {}


@pytest_asyncio.fixture
async def hass(event_loop, tmp_path) -> HomeAssistant:
    hass = HomeAssistant(str(tmp_path))
    hass.loop = event_loop
    hass.config_entries = MockConfigEntries()
    return hass
