class FinalReportEngine:


    def generate(
        self,
        market,
        stock,
        option
    ):


        return {

            "market": {

                "view":
                    market.get(
                        "view",
                        "UNKNOWN"
                    ),

                "regime":
                    market.get(
                        "regime",
                        "UNKNOWN"
                    )

            },


            "stock": {

                "symbol":
                    stock.get(
                        "symbol"
                    ),

                "direction":
                    stock.get(
                        "direction"
                    ),

                "confidence":
                    stock.get(
                        "confidence"
                    ),

                "reasons":
                    stock.get(
                        "reasons",
                        []
                    )

            },


            "option": {

                "contract":
                    option.get(
                        "contract"
                    ),

                "expiry":
                    option.get(
                        "expiry",
                        "CURRENT"
                    ),

                "scenario":
                    option.get(
                        "scenario",
                        "Potential ITM movement"
                    ),

                "entry":
                    option.get(
                        "entry"
                    ),

                "target":
                    option.get(
                        "target"
                    ),

                "risk":
                    option.get(
                        "risk",
                        "MEDIUM"
                    )

            }

        }