from app.analyzer.analyzer import StockAnalyzer
from app.config.provider_factory import get_stock_provider
from app.portfolio.risk_manager import RiskManager
from app.backtesting.backtest_engine import BacktestEngine


def test_backtest_engine_runs():

    provider = get_stock_provider()

    analyzer = StockAnalyzer(
        provider
    )

    risk = RiskManager()

    engine = BacktestEngine(
        analyzer,
        risk,
        provider
    )

    report = engine.run(
        "HAL.NS"
    )

    assert report is not None
    assert report.symbol == "HAL.NS"
    assert report.recommendation
    assert report.opportunity_score
