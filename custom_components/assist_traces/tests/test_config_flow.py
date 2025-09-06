"""Config flow tests are skipped due to missing dependencies."""

import pytest

pytest.skip("config flow requires Home Assistant", allow_module_level=True)
