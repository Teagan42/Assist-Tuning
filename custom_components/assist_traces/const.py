"""Constants for assist_traces integration."""

from __future__ import annotations

DOMAIN = "assist_traces"
DATA_TRACES = "traces"
DATA_WRITER = "writer"
DATA_CORRELATOR = "correlator"
DATA_QUEUE = "queue"

CONF_ENABLED = "enabled"
CONF_REDACTION_LEVEL = "redaction_level"
CONF_SINK_DIR = "sink_dir"
CONF_PARTITIONING = "partitioning"
PARTITION_DAILY = "daily"
PARTITION_HOURLY = "hourly"

DEFAULT_SINK_DIR = "/config/assist_traces/ndjson"
DEFAULT_PARTITIONING = PARTITION_DAILY
DEFAULT_REDACTION = "basic"
DEFAULT_QUEUE_SIZE = 4096
DEFAULT_MAX_FILE_MB = 64
