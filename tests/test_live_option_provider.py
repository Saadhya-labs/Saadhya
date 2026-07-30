import pytest
import requests

from app.data.providers.nse_option_provider import NSEOptionProvider


def test_live_option_provider():

    provider = NSEOptionProvider()

    try:
        options = provider.get_option_chain("HAL")

    except requests.HTTPError as exc:
        pytest.skip(f"NSE rejected the request: {exc}")

    assert len(options) > 0