from __future__ import annotations

import gzip
import json

import pytest

from custom_components.assist_traces import async_setup_entry
from custom_components.assist_traces.const import DATA_TRACES, DOMAIN
from custom_components.assist_traces.tests.conftest import MockConfigEntry


@pytest.mark.asyncio
async def test_log_event_and_feedback(hass, tmp_path):
    entry = MockConfigEntry(options={})
    await async_setup_entry(hass, entry)

    trace = {"trace_id": "abc", "ts": "2024-06-01T00:00:00", "model": "m"}
    await hass.services.async_call(DOMAIN, "log_event", {"trace": trace}, blocking=True)
    await hass.services.async_call(
        DOMAIN,
        "log_event",
        {"trace": {"trace_id": "abc", "ts": "2024-06-01T00:00:00", "model": "m", "response_text": "ok"}},
        blocking=True,
    )
    assert hass.data[DATA_TRACES]["abc"]["response_text"] == "ok"

    await hass.services.async_call(DOMAIN, "set_feedback", {"trace_id": "abc", "feedback": "up"}, blocking=True)
    assert hass.data[DATA_TRACES]["abc"]["user_feedback"] == "up"

    out_path = tmp_path / "out.jsonl.gz"
    await hass.services.async_call(
        DOMAIN,
        "export_sft",
        {"output_path": str(out_path), "dedup": "none"},
        blocking=True,
    )
    assert out_path.exists()
    with gzip.open(out_path, "rb") as f:
        line = f.readline()
        row = json.loads(line)
    assert row["instruction"] is None
