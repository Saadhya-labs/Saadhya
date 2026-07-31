from app.scanner.opportunity_ranker import OpportunityRanker


class MarketScanner:


    def __init__(
        self,
        stock_scanner,
        option_scanner
    ):

        self.stock_scanner = stock_scanner

        self.option_scanner = option_scanner

        self.rank_engine = OpportunityRanker()



    def scan(self):


        stock_results = self.stock_scanner.scan()


        option_results = self.option_scanner.scan()



        opportunities = []



        # -------------------------
        # Stocks
        # -------------------------

        for stock in stock_results:


            opportunities.append(

                {

                    "type": "STOCK",

                    "symbol":
                        stock["symbol"],

                    "score":
                        stock.get(
                            "score",
                            0
                        ),

                    "details":
                        stock

                }

            )



        # -------------------------
        # Options
        # -------------------------

        for option in option_results:


            score = option.get(
                "probability",
                {}
            ).get(
                "score",
                0
            )


            opportunities.append(

                {

                    "type": "OPTION",

                    "symbol":
                        option["symbol"],

                    "score":
                        score,

                    "details":
                        option

                }

            )



        ranked = self.rank_engine.rank(

            opportunities

        )


        return ranked