class OptionMarketScanner:


    def __init__(
        self,
        stock_scanner,
        analyzer,
        option_provider,
        option_scanner
    ):

        self.stock_scanner = stock_scanner
        self.analyzer = analyzer
        self.option_provider = option_provider
        self.option_scanner = option_scanner



    def scan(self):

        opportunities = []


        stocks = self.stock_scanner.scan()


        for stock in stocks:

            symbol = stock["symbol"]


            print(
                f"Analyzing {symbol}"
            )


            report = self.analyzer.analyze(
                symbol
            )


            options = self.option_provider.get_option_chain(
                symbol.replace(".NS", "")
            )


            ranked = self.option_scanner.scan(
                options,
                report.direction
            )


            if ranked:

                opportunities.append(

                    {
                        "symbol": symbol,

                        "direction":
                            report.direction,

                        "option":
                            ranked[0]

                    }

                )


        return opportunities