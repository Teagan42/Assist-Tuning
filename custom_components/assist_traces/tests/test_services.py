"""Service tests are skipped due to missing dependencies."""

import pytest

pytest.skip("services require pydantic and full HA", allow_module_level=True)
