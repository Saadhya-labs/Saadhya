class MarketRegime:


    def detect(
        self,
        snapshot
    ):


        trend = snapshot["trend"]


        if trend == "BULLISH":

            return {

                "regime": "RISK_ON",

                "option_preference":
                    "CALLS",

                "description":
                    "Bullish market conditions"

            }



        if trend == "BEARISH":

            return {

                "regime": "RISK_OFF",

                "option_preference":
                    "PUTS",

                "description":
                    "Bearish market conditions"

            }



        return {

            "regime":"NEUTRAL",

            "option_preference":
                "WAIT",

            "description":
                "Sideways market conditions"

        }