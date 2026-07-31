class MarketAdjustment:


    def adjust(
        self,
        option_score,
        market_regime,
        option_type
    ):


        bonus = 0


        if (
            market_regime == "RISK_ON"
            and option_type == "CE"
        ):
            bonus = 10


        elif (
            market_regime == "RISK_OFF"
            and option_type == "PE"
        ):
            bonus = 10


        return min(
            option_score + bonus,
            100
        )