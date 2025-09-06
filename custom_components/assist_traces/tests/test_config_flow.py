from __future__ import annotations

import pytest

from custom_components.assist_traces.config_flow import AssistTracesConfigFlow
from custom_components.assist_traces.const import CONF_ENABLED, CONF_REDACTION_LEVEL


@pytest.mark.asyncio
async def test_flow(hass):
    flow = AssistTracesConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user()
    assert result["type"] == "form"
    result2 = await flow.async_step_user(
        {CONF_ENABLED: True, CONF_REDACTION_LEVEL: "basic"}
    )
    assert result2["type"] == "create_entry"
