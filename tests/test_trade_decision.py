from app.analyzer.analyzer import StockAnalyzer
from app.strategy.trade_decision import TradeDecision


def test_trade_decision_generation():

    analyzer = StockAnalyzer()

    report = analyzer.analyze(
        "HAL.NS"
    )

    engine = TradeDecision()

    decision = engine.calculate(
        report
    )

    assert report.symbol == "HAL.NS"

    assert report.recommendation

    assert isinstance(decision, dict)

    assert "action" in decision

    # Optional fields may be absent depending on the action,
    # but the decision object itself must always exist.
    assert decision["action"]