from app.scanner.option_market_scanner import OptionMarketScanner
from app.data.mock_option_provider import MockOptionProvider
from app.options.scanner import OptionScanner


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
            pass


        report = Report()

        report.direction = "BUY"
        report.confidence = 90
        report.symbol = symbol


        return report



scanner = OptionMarketScanner(

    DummyStockScanner(),

    DummyAnalyzer(),

    MockOptionProvider(),

    OptionScanner()

)



results = scanner.scan()



print("="*60)
print("SAADHYA DAILY OPTION SCAN")
print("="*60)



for item in results:

    print()

    print(
        item["symbol"]
    )

    print(
        item["direction"]
    )

    print(
        item["option"]
    )