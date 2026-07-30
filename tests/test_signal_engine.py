from app.data.providers.mock_stock_provider import MockStockProvider
from app.strategy.signal_engine import SignalEngine


def test_signal_engine_generates_signals():

    provider = MockStockProvider()

    data = provider.get_history("HAL.NS")

    engine = SignalEngine()

    signals = engine.generate(data)

    assert isinstance(signals, dict)

    assert set(signals.keys()) == {
        "EMA",
        "RSI",
        "MACD",
        "VWAP",
        "SUPERTREND",
    }

    for value in signals.values():

        assert value in {
            "BUY",
            "SELL",
            "HOLD",
        }