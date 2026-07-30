from app.scanner.ranked_scanner import RankedScanner
from app.scanner.report_generator import ReportGenerator


def test_report_generator_creates_reports():

    symbols = [
        "HAL.NS",
        "TCS.NS",
        "INFY.NS"
    ]

    scanner = RankedScanner()

    results = scanner.scan(
        symbols
    )

    generator = ReportGenerator()

    reports = generator.generate(
        results
    )

    assert reports

    for item in reports:

        assert item["symbol"]

        assert item["score"] >= 0

        assert item["recommendation"]

        assert item["confidence"] >= 0

        assert "decision" in item

        assert "signals" in item