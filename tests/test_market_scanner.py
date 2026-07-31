from app.scanner.market_scanner import MarketScanner



class DummyStockScanner:


    def scan(self):

        return [

            {
                "symbol": "HAL.NS",
                "score": 90
            }

        ]



class DummyOptionScanner:


    def scan(self):

        return [

            {

                "symbol": "HAL.NS",

                "probability": {

                    "score": 95

                }

            }

        ]



def test_market_scanner_combines_opportunities():


    scanner = MarketScanner(

        DummyStockScanner(),

        DummyOptionScanner()

    )


    result = scanner.scan()


    assert len(result) == 2

    assert result[0]["score"] >= result[1]["score"]

    assert result[0]["rank"] == 1