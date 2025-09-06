"""Config flow for assist_traces."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_ENABLED, CONF_REDACTION_LEVEL, DOMAIN, DEFAULT_REDACTION


class AssistTracesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Assist Traces", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_ENABLED, default=True): bool,
            vol.Required(CONF_REDACTION_LEVEL, default=DEFAULT_REDACTION): vol.In(["none", "basic", "strict"]),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input):
        return await self.async_step_user(user_input)

    async def async_get_options_flow(self, config_entry):
        return AssistTracesOptionsFlow(config_entry)


class AssistTracesOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_ENABLED, default=self.entry.options.get(CONF_ENABLED, True)): bool,
            vol.Required(CONF_REDACTION_LEVEL, default=self.entry.options.get(CONF_REDACTION_LEVEL, DEFAULT_REDACTION)): vol.In(["none", "basic", "strict"]),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
