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


def test_analyzer_propagates_provider_company_name():
    class NamedProvider(MockStockProvider):
        def get_company_name(self, symbol):
            assert symbol == "HAL.NS"
            return "HINDUSTAN AERONAUTICS LIMITED"

    report = StockAnalyzer(NamedProvider()).analyze("HAL.NS")

    assert report.company_name == "HINDUSTAN AERONAUTICS LIMITED"


def test_company_name_lookup_failure_does_not_drop_cached_analysis():
    class ReconnectingProvider(MockStockProvider):
        def get_company_name(self, _symbol):
            raise RuntimeError("instrument master temporarily unavailable")

    report = StockAnalyzer(ReconnectingProvider()).analyze("HAL.NS")

    assert report.symbol == "HAL.NS"
    assert report.company_name == ""
    assert report.price == 154.0
