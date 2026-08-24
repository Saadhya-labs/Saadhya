import pytest
import requests

from app.data.providers.nse_option_provider import NSEOptionProvider


@pytest.mark.live
def test_live_option_provider():

    provider = NSEOptionProvider()

    try:
        options = provider.get_option_chain("HAL")

    except requests.RequestException as exc:
        pytest.skip(f"NSE is unavailable: {exc}")

    assert len(options) > 0
