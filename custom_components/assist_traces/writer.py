"""Async trace writer."""

from __future__ import annotations

import asyncio
import gzip
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .const import DEFAULT_MAX_FILE_MB, DEFAULT_PARTITIONING, PARTITION_HOURLY


@dataclass
class WriterConfig:
    """Configuration for TraceWriter."""

    directory: str
    partitioning: str = DEFAULT_PARTITIONING
    max_file_mb: int = DEFAULT_MAX_FILE_MB


class TraceWriter:
    """Background writer writing traces to gzipped JSONL files."""

    def __init__(self, config: WriterConfig) -> None:
        """Initialize the writer with configuration."""
        self.config = config
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None
        self._current_path: Optional[Path] = None
        self._current_file: Optional[gzip.GzipFile] = None
        self._current_size = 0

    async def start(self) -> None:
        """Start the background writer task."""
        if self._task is None:
            self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        """Stop the background writer and close files."""
        if self._task:
            await self.queue.put(None)  # type: ignore[arg-type]
            await self._task
            self._task = None
        if self._current_file:
            self._current_file.close()

    async def enqueue(self, trace: Dict[str, Any]) -> None:
        """Enqueue a trace for writing."""
        await self.queue.put(trace)

    async def flush(self) -> None:
        """Flush and rotate the current file if open."""
        if self._current_file:
            self._current_file.close()
            self._current_file = None
            self._current_size = 0
            self._current_path = None

    async def _worker(self) -> None:
        """Consume items from the queue and write them to disk."""
        while True:
            item = await self.queue.get()
            if item is None:
                break
            await asyncio.get_running_loop().run_in_executor(
                None, self._write_line, item
            )
            self.queue.task_done()

    def _partition_path(self, trace: Dict[str, Any]) -> Path:
        """Return the partitioned path for a trace."""
        ts: datetime = datetime.fromisoformat(trace["ts"]).replace(tzinfo=None)
        parts = [
            self.config.directory,
            f"{ts.year:04d}",
            f"{ts.month:02d}",
            f"{ts.day:02d}",
        ]
        if self.config.partitioning == PARTITION_HOURLY:
            parts.append(f"{ts.hour:02d}")
        model = trace.get("model", "unknown")
        parts.append(f"model={model}")
        directory = Path(os.path.join(*parts))
        directory.mkdir(parents=True, exist_ok=True)
        return directory / "part.jsonl.gz"

    def _open_file(self, path: Path) -> None:
        """Open a gzip file for appending."""
        self._current_file = gzip.open(path, "ab")
        self._current_path = path
        self._current_size = path.stat().st_size if path.exists() else 0

    def _write_line(self, trace: Dict[str, Any]) -> None:
        """Write a single trace line to the current partition."""
        path = self._partition_path(trace)
        if self._current_path != path or self._current_file is None:
            if self._current_file:
                self._current_file.close()
            self._open_file(path)
        line = json.dumps(trace, ensure_ascii=False).encode("utf-8") + b"\n"
        self._current_file.write(line)
        self._current_size += len(line)
        if self._current_size > self.config.max_file_mb * 1024 * 1024:
            self._current_file.close()
            self._current_file = None
            self._current_path = None
            self._current_size = 0
