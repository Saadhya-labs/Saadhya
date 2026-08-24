import pytest

from app.data.providers.nse_stock_provider import NSEStockProvider


@pytest.mark.live
def test_live_stock_provider_returns_price_and_history():
    provider = NSEStockProvider()
    try:
        price = provider.get_price("HAL.NS")
        history = provider.get_history("HAL.NS")
    except ValueError as exc:
        pytest.skip(f"Live market data is unavailable: {exc}")

    assert price > 0
    assert not history.empty
