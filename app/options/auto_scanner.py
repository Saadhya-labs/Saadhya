class AutomaticOptionScanner:


    def __init__(
        self,
        option_provider,
        option_scanner,
        smart_ranker
    ):

        self.provider = option_provider
        self.option_scanner = option_scanner
        self.smart_ranker = smart_ranker



    def scan(
        self,
        stock_report
    ):


        options = self.provider.get_option_chain(
            stock_report.symbol.replace(".NS","")
        )


        direction = stock_report.direction


        ranked = self.option_scanner.scan(
            options,
            direction
        )


        if not ranked:

            return None


        best = ranked[0]


        result = self.smart_ranker.calculate(
            stock_report,
            best
        )


        return result