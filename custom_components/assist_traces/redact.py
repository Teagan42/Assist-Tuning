"""Redaction utilities."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable

BASIC_PATTERNS = {
    "<EMAIL>": re.compile(r"[\w.%-]+@[\w.-]+"),
    "<PHONE>": re.compile(r"\+?\d[\d\s-]{7,}\d"),
    "<IP>": re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
    "<MAC>": re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    "<URL>": re.compile(r"https?://\S+"),
    "<SSID>": re.compile(r"ssid-\w+", re.IGNORECASE),
    "<ADDR>": re.compile(r"\d{1,4} [A-Za-z0-9 .]{3,}"),
}

STRICT_KEYS = {"user", "owner", "household_members", "user_id"}


def _redact_string(text: str, patterns: Dict[str, re.Pattern]) -> str:
    """Replace occurrences of patterns in a string with tokens."""
    for token, pattern in patterns.items():
        text = pattern.sub(token, text)
    return text


def _redact_recursive(
    data: Any, patterns: Dict[str, re.Pattern], names: Iterable[str]
) -> Any:
    """Recursively redact strings within nested structures."""
    if isinstance(data, str):
        red = _redact_string(data, patterns)
        for idx, name in enumerate(names):
            if name and name.lower() in red.lower():
                red = re.sub(re.escape(name), f"<NAME_{idx}>", red, flags=re.IGNORECASE)
        return red
    if isinstance(data, list):
        return [_redact_recursive(v, patterns, names) for v in data]
    if isinstance(data, dict):
        new = {}
        for k, v in data.items():
            new_key = _redact_string(k, patterns)
            names_for_field = names
            if k in STRICT_KEYS and isinstance(v, str):
                names_for_field = list(names) + [v]
            new[new_key] = _redact_recursive(v, patterns, names_for_field)
        return new
    return data


def redact(
    data: Dict[str, Any], level: str, known_names: Iterable[str] | None = None
) -> Dict[str, Any]:
    """Redact PII from dictionary."""
    if level == "none":
        return data
    patterns = BASIC_PATTERNS if level in {"basic", "strict"} else {}
    names: Iterable[str] = known_names or []
    return _redact_recursive(data, patterns, names)
