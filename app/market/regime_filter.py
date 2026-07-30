class MarketRegimeFilter:


    def analyze(
        self,
        nifty,
        banknifty,
        vix
    ):


        bullish = 0
        bearish = 0



        # NIFTY

        if nifty == "BULLISH":

            bullish += 1

        elif nifty == "BEARISH":

            bearish += 1



        # BANKNIFTY

        if banknifty == "BULLISH":

            bullish += 1

        elif banknifty == "BEARISH":

            bearish += 1



        # VIX

        if vix == "LOW":

            bullish += 1

        elif vix == "HIGH":

            bearish += 1



        if bullish >= 2:

            regime = "BULLISH"

            adjustment = 10


        elif bearish >= 2:

            regime = "BEARISH"

            adjustment = -15


        else:

            regime = "NEUTRAL"

            adjustment = 0



        return {

            "regime": regime,

            "confidence_adjustment": adjustment,

            "details": {

                "nifty": nifty,

                "banknifty": banknifty,

                "vix": vix

            }

        }