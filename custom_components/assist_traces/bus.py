"""Optional message bus publisher."""
from __future__ import annotations

from typing import Any, Dict, List


class BusPublisher:
    """Very small stub publisher used in tests."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.type = config.get("type", "none")
        self.published: List[Dict[str, Any]] = []

    async def publish(self, trace: Dict[str, Any]) -> None:
        if self.type == "none":
            return
        self.published.append(trace)

    async def close(self) -> None:
        return
