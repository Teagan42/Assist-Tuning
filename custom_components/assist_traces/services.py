"""Service handlers for assist_traces."""
from __future__ import annotations

import gzip
import json
from datetime import datetime
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DATA_TRACES, DATA_WRITER, DOMAIN
from .helpers import dedup_simhash, summarize_context
from .models import AssistTrace
from .redact import redact


def _merge(existing: Dict[str, Any], update: Dict[str, Any]) -> None:
    for k, v in update.items():
        if isinstance(v, dict) and isinstance(existing.get(k), dict):
            _merge(existing[k], v)
        elif isinstance(v, list) and isinstance(existing.get(k), list):
            existing[k].extend(v)
        else:
            existing[k] = v


async def async_setup_services(hass: HomeAssistant) -> None:
    async def log_event(call: ServiceCall) -> None:
        payload: Dict[str, Any] = call.data.get("trace", {})
        trace = AssistTrace.model_validate(payload).model_dump(mode="json")
        traces = hass.data.setdefault(DATA_TRACES, {})
        existing = traces.get(trace["trace_id"])
        if existing:
            _merge(existing, trace)
            merged = existing
        else:
            traces[trace["trace_id"]] = trace
            merged = trace
        redacted = redact(dict(merged), hass.data[DOMAIN]["redaction_level"])  # type: ignore[index]
        await hass.data[DATA_WRITER].enqueue(redacted)
        pa = merged.get("parsed_action") or {}
        entity_ids = []
        target = pa.get("target") or {}
        if isinstance(target, dict) and target.get("entity_id"):
            eids = target.get("entity_id")
            if isinstance(eids, list):
                entity_ids.extend(eids)
            else:
                entity_ids.append(eids)
        if entity_ids:
            await hass.data[DOMAIN]["correlator"].add_trace(trace["trace_id"], entity_ids)  # type: ignore[index]

    async def set_feedback(call: ServiceCall) -> None:
        trace_id = call.data["trace_id"]
        trace = hass.data[DATA_TRACES].get(trace_id)
        if trace:
            trace["user_feedback"] = call.data.get("feedback")
            trace["repair_text"] = call.data.get("repair_text")
            trace["gold_action"] = call.data.get("gold_action")

    async def export_sft(call: ServiceCall) -> None:
        output_path = call.data.get("output_path") or f"/config/assist_traces/datasets/sft-{datetime.utcnow():%Y%m%d}.jsonl.gz"
        traces = list(hass.data[DATA_TRACES].values())
        rows = []
        for tr in traces:
            rows.append(
                {
                    "instruction": tr.get("user_text", ""),
                    "context": summarize_context(tr.get("context", {})),
                    "output": tr.get("gold_action") or tr.get("parsed_action"),
                    "source": "gold" if tr.get("gold_action") else "implicit_success",
                    "trace_id": tr.get("trace_id"),
                }
            )
        texts = [json.dumps(r) for r in rows]
        deduped = dedup_simhash(texts) if call.data.get("dedup") == "simhash" else texts
        with gzip.open(output_path, "wb") as f:
            for line in deduped:
                f.write(line.encode() + b"\n")

    async def export_prefs(call: ServiceCall) -> None:
        output_path = call.data.get("output_path") or f"/config/assist_traces/datasets/prefs-{datetime.utcnow():%Y%m%d}.jsonl.gz"
        traces = list(hass.data[DATA_TRACES].values())
        rows = []
        for tr in traces:
            rows.append(
                {
                    "prompt": tr.get("user_text", ""),
                    "context": summarize_context(tr.get("context", {})),
                    "chosen": tr.get("gold_action") or tr.get("parsed_action"),
                    "rejected": tr.get("parsed_action"),
                    "trace_id": tr.get("trace_id"),
                }
            )
        with gzip.open(output_path, "wb") as f:
            for line in rows:
                f.write(json.dumps(line).encode() + b"\n")

    async def flush(call: ServiceCall) -> None:
        await hass.data[DATA_WRITER].flush()

    hass.services.async_register(DOMAIN, "log_event", log_event)
    hass.services.async_register(DOMAIN, "set_feedback", set_feedback)
    hass.services.async_register(DOMAIN, "export_sft", export_sft)
    hass.services.async_register(DOMAIN, "export_prefs", export_prefs)
    hass.services.async_register(DOMAIN, "flush", flush)
