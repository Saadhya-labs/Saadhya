from app.backtesting.historical_runner import HistoricalBacktestRunner
from app.data.providers.mock_stock_provider import MockStockProvider



def test_historical_backtest():


    provider = MockStockProvider()


    runner = HistoricalBacktestRunner(
        provider
    )


    result = runner.run(
        "HAL.NS"
    )


    assert result is not None

    assert result["trades"] == 1

    assert result["net_profit"] > 0