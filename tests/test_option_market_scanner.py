from app.scanner.option_market_scanner import OptionMarketScanner
from app.data.mock_option_provider import MockOptionProvider
from app.options.scanner import OptionScanner
from app.strategy.probability_engine import ProbabilityEngine
from app.options.models import OptionContract



class DummyStockScanner:


    def scan(self):

        return [

            {
                "symbol": "HAL.NS"
            },

            {
                "symbol": "TCS.NS"
            }

        ]



class DummyAnalyzer:


    def analyze(self, symbol):

        class Report:

            direction = "BUY"


        return Report()



class DummyMarketRegime:

    regime = "BULLISH"



scanner = OptionMarketScanner(

    DummyStockScanner(),

    DummyAnalyzer(),

    MockOptionProvider(),

    OptionScanner(),

    ProbabilityEngine(),

    DummyMarketRegime()

)



results = scanner.scan()



print("="*60)

print("SAADHYA DAILY OPTION SCAN")

print("="*60)



for item in results:


    print()

    print(
        item["formatted_report"]
    )


def test_scanner_returns_one_recommendation_for_each_of_three_expiries():
    class OneStock:
        def scan(self):
            return [{"symbol": "NIFTY"}]

    class ThreeExpiries:
        def get_option_chain(self, _symbol):
            return [
                OptionContract("NIFTY", expiry, 25000, "CE", 100, 100000, 200000, 20, .5, -.1)
                for expiry in ("2026-09-03", "2026-09-10", "2026-09-17")
            ]

    scanner = OptionMarketScanner(
        OneStock(), DummyAnalyzer(), ThreeExpiries(), OptionScanner(),
        ProbabilityEngine(), DummyMarketRegime(),
    )

    recommendations = scanner.scan()

    assert [item["expiry"] for item in recommendations] == [
        "2026-09-03", "2026-09-10", "2026-09-17"
    ]
    assert [item["expiry_rank"] for item in recommendations] == [1, 2, 3]
    assert {item["data_status"] for item in recommendations} == {"fresh"}
    assert scanner.coverage == [{
        "symbol": "NIFTY",
        "underlying": "NIFTY",
        "status": "fresh",
        "expiries": ["2026-09-03", "2026-09-10", "2026-09-17"],
        "contract_count": 3,
        "recommendation_count": 3,
    }]


def test_scanner_prefetches_all_underlyings_through_batch_provider():
    class TwoStocks:
        def scan(self):
            return [{"symbol": "HAL.NS"}, {"symbol": "NIFTY"}]

    class BatchProvider:
        stale_symbols = set()
        chain_failures = {}
        chain_updated_at = {
            "HAL": "2026-09-08T12:00:00+00:00",
            "NIFTY": "2026-09-08T12:00:01+00:00",
        }

        def __init__(self):
            self.calls = []

        def get_option_chains(self, symbols):
            symbols = tuple(symbols)
            self.calls.append(symbols)
            return {
                symbol: [
                    OptionContract(
                        symbol, expiry, 100, "CE", 10, 100000, 200000, 20, .5, -.1
                    )
                    for expiry in ("2026-09-03", "2026-09-10", "2026-09-17")
                ]
                for symbol in symbols
            }

        def get_option_chain(self, _symbol):
            raise AssertionError("per-symbol option fetching should not be used")

    provider = BatchProvider()
    scanner = OptionMarketScanner(
        TwoStocks(), DummyAnalyzer(), provider, OptionScanner(),
        ProbabilityEngine(), DummyMarketRegime(),
    )

    recommendations = scanner.scan()

    assert provider.calls == [("HAL", "NIFTY")]
    assert len(recommendations) == 6
    assert {
        item["updated_at"] for item in recommendations if item["symbol"] == "HAL.NS"
    } == {"2026-09-08T12:00:00+00:00"}


def test_scanner_marks_cached_option_recommendations_explicitly():
    class OneStock:
        def scan(self):
            return [{"symbol": "HAL.NS"}]

    class CachedProvider:
        stale_symbols = {"HAL"}
        chain_failures = {}
        chain_updated_at = {"HAL": "2026-09-08T11:50:00+00:00"}

        def get_option_chains(self, _symbols):
            return {"HAL": [
                OptionContract(
                    "HAL", "2026-09-24", 100, "CE", 10,
                    100000, 200000, 20, .5, -.1,
                )
            ]}

    scanner = OptionMarketScanner(
        OneStock(), DummyAnalyzer(), CachedProvider(), OptionScanner(),
        ProbabilityEngine(), DummyMarketRegime(),
    )

    recommendations = scanner.scan()

    assert {item["data_status"] for item in recommendations} == {"cached"}


def test_scanner_warns_when_contract_master_is_cached_but_quotes_are_fresh():
    class OneStock:
        def scan(self):
            return [{"symbol": "HAL.NS"}]

    class CachedMasterProvider:
        stale_symbols = set()
        chain_failures = {}
        chain_updated_at = {"HAL": "2026-09-13T12:00:00+00:00"}
        instrument_master_stale = True

        def get_option_chains(self, _symbols):
            return {"HAL": [
                OptionContract(
                    "HAL", "2026-09-24", 100, "CE", 10,
                    100000, 200000, 20, .5, -.1,
                )
            ]}

    scanner = OptionMarketScanner(
        OneStock(), DummyAnalyzer(), CachedMasterProvider(), OptionScanner(),
        ProbabilityEngine(), DummyMarketRegime(),
    )

    recommendations = scanner.scan()

    assert recommendations[0]["data_status"] == "fresh"
    assert any(
        "last-known-good Kite instrument master" in warning
        for warning in recommendations[0]["warnings"]
    )
    assert scanner.coverage[0]["instrument_master_status"] == "cached"


def test_scanner_keeps_only_direction_aligned_contract_per_underlying():
    class OneIndex:
        def scan(self):
            return [{"symbol": "HAL.NS"}]

    class BothSides:
        def get_option_chain(self, _symbol):
            return [
                OptionContract("HAL", "2026-09-29", 25000, side, 100, 600000, 1500000, 20, .5, -.1)
                for side in ("CE", "PE")
            ]

    scanner = OptionMarketScanner(
        OneIndex(), DummyAnalyzer(), BothSides(), OptionScanner(),
        ProbabilityEngine(), DummyMarketRegime(),
    )
    recommendations = scanner.scan()
    assert {item["option"]["option"].option_type for item in recommendations} == {"CE"}
