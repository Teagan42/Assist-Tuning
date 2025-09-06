from __future__ import annotations

from custom_components.assist_traces.redact import redact


def test_basic_redaction():
    data = {"msg": "Email me at test@example.com", "ip": "10.1.1.1"}
    out = redact(data, "basic")
    assert out["msg"] == "Email me at <EMAIL>"
    assert out["ip"] == "<IP>"


def test_strict_redaction_names():
    data = {"user": "Teagan", "msg": "Teagan did it"}
    out = redact(data, "strict", ["Teagan"])
    assert out["user"] == "<NAME_0>"
    assert out["msg"] == "<NAME_0> did it"
