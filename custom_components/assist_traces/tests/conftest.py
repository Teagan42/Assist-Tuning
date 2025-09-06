"""Pytest fixtures and Home Assistant stubs."""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from typing import Any, Callable, Dict

import pytest
import pytest_asyncio

# ---------------------------------------------------------------------------
# Minimal Home Assistant core stubs
# ---------------------------------------------------------------------------
ha = types.ModuleType("homeassistant")
core = types.ModuleType("homeassistant.core")


class ServiceCall:
    """Container for service data."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data


class ServiceRegistry:
    """Very small service registry used in tests."""

    def __init__(self, hass: "HomeAssistant") -> None:
        self._hass = hass
        self._handlers: Dict[str, Dict[str, Callable[[ServiceCall], Any]]] = {}

    def async_register(self, domain: str, service: str, handler) -> None:
        """Register a service handler."""
        self._handlers.setdefault(domain, {})[service] = handler

    async def async_call(
        self, domain: str, service: str, data: Dict[str, Any], *, blocking: bool = False
    ) -> None:
        """Invoke a registered service."""
        handler = self._handlers[domain][service]
        call = ServiceCall(data)
        if asyncio.iscoroutinefunction(handler):
            coro = handler(call)
        else:

            async def _sync() -> None:
                handler(call)

            coro = _sync()
        if blocking:
            await coro
        else:
            self._hass.async_create_task(coro)


class HomeAssistant:
    """Minimal Home Assistant implementation for tests."""

    def __init__(self, config_path: str) -> None:
        self.config = types.SimpleNamespace(path=config_path)
        self.data: Dict[str, Any] = {}
        self.loop = asyncio.get_event_loop()
        self.services = ServiceRegistry(self)
        self.config_entries = None  # populated in fixtures

    def async_create_task(self, coro):
        """Schedule a coroutine on the event loop."""
        return self.loop.create_task(coro)


core.HomeAssistant = HomeAssistant
core.ServiceCall = ServiceCall
core.callback = lambda func: func
ha.core = core
sys.modules.setdefault("homeassistant", ha)
sys.modules.setdefault("homeassistant.core", core)

# Ensure repository root is importable for ``custom_components`` namespace
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

config_entries = types.ModuleType("homeassistant.config_entries")


class ConfigFlow:
    """Base class for configuration flows."""

    async def async_step_user(self, user_input=None):
        raise NotImplementedError

    def async_create_entry(self, title, data):
        return {"type": "create_entry"}

    def async_show_form(self, step_id, data_schema):
        return {"type": "form"}


class OptionsFlow:
    """Base class for options flows."""

    async def async_step_init(self, user_input=None):
        raise NotImplementedError

    def async_create_entry(self, title, data):
        return {"type": "create_entry"}

    def async_show_form(self, step_id, data_schema):
        return {"type": "form"}


class ConfigEntry:
    """Placeholder for Home Assistant's ConfigEntry."""

    def __init__(self, options: Dict[str, Any] | None = None) -> None:
        self.options = options or {}


config_entries.ConfigFlow = ConfigFlow
config_entries.OptionsFlow = OptionsFlow
config_entries.ConfigEntry = ConfigEntry
sys.modules.setdefault("homeassistant.config_entries", config_entries)

# ---------------------------------------------------------------------------
# Stub modules required by the integration
# ---------------------------------------------------------------------------
sys.modules.setdefault("hass_nabucasa", types.ModuleType("hass_nabucasa"))
sys.modules.setdefault("hass_nabucasa.remote", types.ModuleType("remote"))
sys.modules.setdefault("hass_nabucasa.acme", types.ModuleType("acme"))

hassil = types.ModuleType("hassil")
hassil.__path__ = []  # type: ignore[attr-defined]
expression = types.ModuleType("hassil.expression")
intents = types.ModuleType("hassil.intents")


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

vol = types.ModuleType("voluptuous")
vol.Schema = lambda schema: schema
vol.Required = lambda key, default=None: key
vol.In = lambda options: list
sys.modules.setdefault("voluptuous", vol)

ws_api = types.ModuleType("homeassistant.components.websocket_api")


def websocket_command(schema):
    def decorator(func):
        return func

    return decorator


def async_register_command(hass, func):
    hass.data.setdefault("ws_cmds", []).append(func)


ws_api.websocket_command = websocket_command
ws_api.async_register_command = async_register_command
components = types.ModuleType("homeassistant.components")
components.websocket_api = ws_api
sys.modules.setdefault("homeassistant.components", components)
sys.modules.setdefault("homeassistant.components.websocket_api", ws_api)


@pytest.fixture
def event_loop():
    """Provide an isolated event loop for each test."""
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

    def __init__(self, options: Dict[str, Any] | None = None) -> None:
        self.options = options or {}


@pytest_asyncio.fixture
async def hass(event_loop, tmp_path) -> HomeAssistant:
    """Return a Home Assistant instance for testing."""
    instance = HomeAssistant(str(tmp_path))
    instance.loop = event_loop
    instance.config_entries = MockConfigEntries()
    return instance
