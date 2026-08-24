import pytest

from app.data.providers.mock_stock_provider import MockStockProvider
from app.data.providers.nse_stock_provider import NSEStockProvider

def test_mock_stock_provider_returns_normalized_history():
    provider = MockStockProvider()

    assert provider.get_price("HAL.NS") > 0
    assert {"Open", "High", "Low", "Close", "Volume"}.issubset(
        provider.get_history("HAL.NS").columns
    )


@pytest.mark.live
def test_live_stock_provider_returns_a_price():
    try:
        price = NSEStockProvider().get_price("HAL.NS")
    except ValueError as exc:
        pytest.skip(f"Live market data is unavailable: {exc}")

    assert price > 0
