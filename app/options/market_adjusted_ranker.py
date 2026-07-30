class MarketAdjustedRanker:


    def calculate(
        self,
        smart_result,
        market_context
    ):

        base_score = smart_result["final_score"]

        adjustment = market_context["confidence_adjustment"]


        final_score = base_score + adjustment


        final_score = max(
            0,
            min(final_score,100)
        )


        return {

            "symbol":
                smart_result["symbol"],

            "option":
                smart_result["option"],

            "base_score":
                base_score,

            "market_adjustment":
                adjustment,

            "final_score":
                final_score,

            "market":
                market_context["regime"]

        }