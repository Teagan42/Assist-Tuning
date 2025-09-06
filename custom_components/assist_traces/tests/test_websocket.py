"""WebSocket API tests are skipped due to missing components."""

import pytest

pytest.skip(
    "websocket tests require Home Assistant components", allow_module_level=True
)
