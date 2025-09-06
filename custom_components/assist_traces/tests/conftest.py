"""Pytest fixtures."""

from __future__ import annotations

import pytest
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from homeassistant.core import HomeAssistant
import pytest_asyncio

# Stub hass_nabucasa to avoid heavy dependencies
sys.modules.setdefault("hass_nabucasa", types.ModuleType("hass_nabucasa"))
sys.modules.setdefault("hass_nabucasa.remote", types.ModuleType("remote"))
sys.modules.setdefault("hass_nabucasa.acme", types.ModuleType("acme"))

# Stub hassil required by Home Assistant's conversation component
hassil = types.ModuleType("hassil")
hassil.__path__ = []  # type: ignore[attr-defined]
expression = types.ModuleType("hassil.expression")
intents = types.ModuleType("hassil.intents")
recognize = types.ModuleType("hassil.recognize")
util = types.ModuleType("hassil.util")


class Expression:  # noqa: D401
    """Placeholder for hassil.expression.Expression."""


class ListReference:  # noqa: D401
    """Placeholder for hassil.expression.ListReference."""


class Sequence:  # noqa: D401
    """Placeholder for hassil.expression.Sequence."""


class Intents:  # noqa: D401
    """Placeholder for hassil.intents.Intents."""


class SlotList:  # noqa: D401
    """Placeholder for hassil.intents.SlotList."""


class TextSlotList:  # noqa: D401
    """Placeholder for hassil.intents.TextSlotList."""


class WildcardSlotList:  # noqa: D401
    """Placeholder for hassil.intents.WildcardSlotList."""


expression.Expression = Expression
expression.ListReference = ListReference
expression.Sequence = Sequence
intents.Intents = Intents
intents.SlotList = SlotList
intents.TextSlotList = TextSlotList
intents.WildcardSlotList = WildcardSlotList
sys.modules.setdefault("hassil", hassil)
sys.modules.setdefault("hassil.expression", expression)
sys.modules.setdefault("hassil.intents", intents)
recognize.MISSING_ENTITY = None
recognize.RecognizeResult = object
recognize.UnmatchedTextEntity = object
recognize.UnmatchedRangeEntity = object
recognize.recognize_all = lambda *args, **kwargs: []
recognize.PUNCTUATION = ""
sys.modules.setdefault("hassil.recognize", recognize)
util.merge_dict = lambda a, b: {**a, **b}
sys.modules.setdefault("hassil.util", util)
home_assistant_intents = types.ModuleType("home_assistant_intents")
home_assistant_intents.ErrorKey = object
home_assistant_intents.get_intents = lambda *args, **kwargs: {}
home_assistant_intents.get_languages = lambda: []
sys.modules.setdefault("home_assistant_intents", home_assistant_intents)


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

    async def async_forward_entry_setups(self, entry, platforms):
        """Pretend to forward setups for the given entry."""
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
