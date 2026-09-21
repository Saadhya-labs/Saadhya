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


def test_scanner_records_transient_symbol_failure_and_continues():
    class Analyzer:
        def analyze(self, symbol):
            if symbol == "BROKEN.NS":
                raise RuntimeError("temporary Kite disconnect")
            return type("Report", (), {"symbol": symbol, "confidence": 80})()

    scanner = StockScanner(
        analyzer=Analyzer(), symbols=("BROKEN.NS", "HAL.NS")
    )

    results = scanner.scan()

    assert [report.symbol for report in results] == ["HAL.NS"]
    assert scanner.failures == [
        {"symbol": "BROKEN.NS", "error": "temporary Kite disconnect"}
    ]


def test_bounded_parallel_scan_keeps_results_and_failures_deterministic():
    class Analyzer:
        def analyze(self, symbol):
            if symbol == "BROKEN.NS":
                raise RuntimeError("quote unavailable")
            return type("Report", (), {"symbol": symbol, "confidence": 80})()

    scanner = StockScanner(
        analyzer=Analyzer(),
        symbols=("HAL.NS", "BROKEN.NS", "TCS.NS"),
        max_workers=3,
    )
    assert [report.symbol for report in scanner.scan()] == ["HAL.NS", "TCS.NS"]
    assert scanner.failures == [{"symbol": "BROKEN.NS", "error": "quote unavailable"}]
