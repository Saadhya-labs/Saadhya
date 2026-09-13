from io import StringIO
from types import SimpleNamespace

from app.cli.market_scan import build_market_scanner, run


class DummyScanner:
    option_scanner = SimpleNamespace(
        failures=[],
        coverage=[{
            "symbol": "HAL.NS", "underlying": "HAL", "status": "fresh",
            "expiries": ["CURRENT_MONTH"], "contract_count": 1,
            "recommendation_count": 1,
        }],
    )

    def scan(self):
        option = SimpleNamespace(
            strike=4600,
            option_type="CE",
            premium=120,
            expiry="CURRENT_MONTH",
        )

        return [
            {
                "rank": 1,
                "type": "OPTION",
                "symbol": "HAL.NS",
                "score": 90,
                "details": {
                    "direction": "BUY",
                    "risk": "LOW",
                    "option": {
                        "option": option,
                        "score": 90,
                        "breakdown": {},
                    },
                },
            }
        ]


class DummyApp:
    def __init__(self):
        self.received = None

    def generate_report(self, opportunities, metadata=None):
        self.received = opportunities

        report = {
            "title": "SAADHYA OPPORTUNITY REPORT",
            "total_opportunities": len(opportunities),
            "top_opportunities": [
                {
                    "rank": 1,
                    "type": "OPTION",
                    "symbol": "HAL.NS",
                    "score": 90,
                    "recommendation": "HIGH PROBABILITY OPPORTUNITY",
                    "risk": "LOW",
                }
            ],
        }
        if metadata is not None:
            report["metadata"] = metadata
        return report


def test_market_scan_uses_existing_scanner_and_report_pipeline():
    app = DummyApp()
    output = StringIO()

    report = run(DummyScanner(), app, output)

    rendered = output.getvalue()

    assert app.received is not None
    assert report["total_opportunities"] == 1
    assert report["metadata"]["option_analysis"] == DummyScanner.option_scanner.coverage
    assert "SAADHYA OPPORTUNITY REPORT" in rendered
    assert "Entry zone: 108.00–132.00" in rendered
    assert "Target zone: 180.00–240.00" in rendered
    assert "no orders are placed" in rendered


def test_market_scan_supports_json_output():
    app = DummyApp()
    output = StringIO()

    run(DummyScanner(), app, output, output_format="json")

    assert '"total_opportunities": 1' in output.getvalue()


def test_market_scanner_accepts_desktop_mode_and_symbol_configuration():
    scanner = build_market_scanner(data_mode="mock", symbols=("HAL.NS",))

    assert scanner.stock_scanner._scanner.symbols == ("HAL.NS",)


def test_market_scanner_accepts_persistent_provider_instances():
    stock_provider = object()
    option_provider = object()

    scanner = build_market_scanner(
        data_mode="mock",
        symbols=("HAL.NS",),
        stock_provider=stock_provider,
        option_provider=option_provider,
    )

    assert scanner.stock_scanner._scanner.analyzer.provider is stock_provider
    assert scanner.option_scanner.option_provider is option_provider


def test_market_scan_includes_scanner_failures():
    class FailingStockScanner:
        failures = [{"symbol": "HAL.NS", "error": "Provider unavailable"}]

    class ScannerWithFailure(DummyScanner):
        stock_scanner = FailingStockScanner()

    output = StringIO()
    run(ScannerWithFailure(), DummyApp(), output)

    assert "Unavailable symbols: 1" in output.getvalue()


def test_market_scan_includes_option_source_failures():
    class FailingOptionScanner:
        failures = [{"symbol": "HAL.NS", "source": "option-chain", "error": "Forbidden"}]

    class ScannerWithFailure(DummyScanner):
        option_scanner = FailingOptionScanner()

    output = StringIO()
    run(ScannerWithFailure(), DummyApp(), output)

    assert "Unavailable symbols: 1" in output.getvalue()


def test_market_scan_reports_last_known_good_provider_data():
    class StaleProvider:
        stale_symbols = {"HAL.NS"}

    class ScannerWithStaleData(DummyScanner):
        market_data_providers = {"stock": StaleProvider()}

    report = run(ScannerWithStaleData(), DummyApp(), StringIO())

    assert report["metadata"]["stale_data"] == [
        {"source": "stock", "symbols": ["HAL.NS"]}
    ]


def test_market_scan_ignores_stale_symbols_outside_current_universe():
    class StaleProvider:
        stale_symbols = {"HAL.NS"}

    class ScannerWithOldStaleData(DummyScanner):
        requested_symbols = ("TCS.NS",)
        market_data_providers = {"stock": StaleProvider()}

    report = run(ScannerWithOldStaleData(), DummyApp(), StringIO())

    assert report["metadata"]["stale_data"] == []


def test_market_scan_reports_cached_instrument_master_as_degraded_data():
    class CachedMasterProvider:
        stale_symbols = set()
        instrument_master_stale = True

    class ScannerWithCachedMaster(DummyScanner):
        market_data_providers = {"option": CachedMasterProvider()}

    report = run(ScannerWithCachedMaster(), DummyApp(), StringIO())

    assert report["metadata"]["stale_data"] == [{
        "source": "option",
        "scope": "instrument-master",
        "status": "cached",
    }]
