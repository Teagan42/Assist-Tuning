"""Helper utilities."""
from __future__ import annotations

import hashlib
from typing import Dict, Iterable, List


def summarize_context(ctx: Dict[str, object]) -> Dict[str, object]:
    """Return a shallow copy of context for dataset export."""
    return {k: v for k, v in ctx.items() if isinstance(v, (int, float, str))}


def dedup_simhash(texts: Iterable[str]) -> List[str]:
    """Very small placeholder for simhash dedup."""
    seen = set()
    out: List[str] = []
    for text in texts:
        h = hashlib.sha1(text.encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            out.append(text)
    return out
