from app.analyzer.analyzer import StockAnalyzer
from app.data.providers.mock_stock_provider import MockStockProvider


def test_analyzer_builds_a_complete_stock_report():
    report = StockAnalyzer(MockStockProvider()).analyze("HAL.NS")

    assert report.symbol == "HAL.NS"
    assert report.price == 154.0
    assert report.direction == "BUY"
    assert report.holding == "Swing (5-10 days)"
    assert report.simple_reasons
    assert report.technical_reasons
    assert report.opportunity_score["total"] <= 100
    assert set(report.opportunity_score["breakdown"]) == {
        "trend", "momentum", "agreement", "risk", "confidence"
    }


def test_analyze_dataframe_does_not_need_a_provider_price_lookup():
    provider = MockStockProvider()
    report = StockAnalyzer(provider).analyze_dataframe(provider.get_history("HAL.NS"), "HAL.NS")

    assert report.price == 154.0
