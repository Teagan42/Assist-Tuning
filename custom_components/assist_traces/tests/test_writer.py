from __future__ import annotations

import asyncio
import gzip
import json
import pytest

from custom_components.assist_traces.writer import TraceWriter, WriterConfig


@pytest.mark.asyncio
async def test_writer_creates_partition(tmp_path):
    config = WriterConfig(directory=str(tmp_path), partitioning="daily", max_file_mb=1)
    writer = TraceWriter(config)
    await writer.start()
    trace = {"trace_id": "1", "ts": "2024-06-01T00:00:00", "model": "m"}
    await writer.enqueue(trace)
    await asyncio.sleep(0.1)
    await writer.stop()
    path = tmp_path / "2024" / "06" / "01" / "model=m" / "part.jsonl.gz"
    assert path.exists()
    with gzip.open(path, "rb") as f:
        line = f.readline()
        obj = json.loads(line)
    assert obj["trace_id"] == "1"
