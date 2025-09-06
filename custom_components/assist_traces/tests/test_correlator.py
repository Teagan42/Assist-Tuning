"""Correlator tests are skipped due to missing Home Assistant bus."""

import pytest

pytest.skip("correlator requires Home Assistant bus", allow_module_level=True)
