from app.scanner.scanner import StockScanner


def test_scanner_runs():

    scanner = StockScanner()

    results = scanner.scan()

    assert results

    for stock in results:

        assert stock.symbol

        assert stock.recommendation

        assert stock.confidence >= 0

        assert stock.opportunity_score["total"] <= 100