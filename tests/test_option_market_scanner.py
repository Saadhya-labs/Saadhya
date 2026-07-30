from app.scanner.option_market_scanner import OptionMarketScanner
from app.data.mock_option_provider import MockOptionProvider
from app.options.scanner import OptionScanner
from app.strategy.probability_engine import ProbabilityEngine



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