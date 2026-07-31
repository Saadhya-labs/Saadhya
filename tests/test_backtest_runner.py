from app.backtesting.engine import BacktestRunner


class MockReport:


    symbol = "HAL.NS"

    price = 4500

    direction = "BUY"



def test_backtest_runner():

    runner = BacktestRunner()


    result = runner.execute(
        MockReport(),
        quantity=10
    )


    assert result is not None

    assert result["trades"] == 1