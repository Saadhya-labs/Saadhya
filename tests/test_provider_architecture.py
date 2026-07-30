import pytest
import requests

from app.data.providers.mock_option_provider import MockOptionProvider
from app.data.providers.nse_option_provider import NSEOptionProvider


def test_mock_option_provider():

    provider = MockOptionProvider()

    options = provider.get_option_chain("HAL")

    assert len(options) > 0
    assert options[0].symbol == "HAL"


def test_nse_option_provider():

    provider = NSEOptionProvider()

    try:
        options = provider.get_option_chain("HAL")

    except requests.HTTPError as exc:
        pytest.skip(f"NSE rejected the request: {exc}")

    assert len(options) > 0