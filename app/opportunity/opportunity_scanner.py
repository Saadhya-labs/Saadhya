from app.opportunity.opportunity_report import OpportunityReport


class OpportunityScanner:


    def scan_stock(
        self,
        symbol,
        recommendation
    ):

        return OpportunityReport(

            symbol=symbol,

            instrument_type="STOCK",

            direction=recommendation.get(
                "direction"
            ),

            opportunity=self._classify(
                recommendation.get("confidence",0)
            ),

            confidence=recommendation.get(
                "confidence",
                0
            ),

            reasons=recommendation.get(
                "technical_reasons",
                []
            )

        )


    def scan_option(
        self,
        symbol,
        expiry,
        strike,
        direction,
        confidence
    ):

        return OpportunityReport(

            symbol=symbol,

            instrument_type="OPTION",

            direction=direction,

            opportunity=self._classify(
                confidence
            ),

            confidence=confidence,

            expiry=expiry,

            strike=strike,

            warnings=[
                "Option profitability depends on volatility, theta and market movement."
            ]

        )


    def _classify(
        self,
        confidence
    ):

        if confidence >= 70:

            return "HIGH PROBABILITY"


        if confidence >= 40:

            return "WATCH"


        return "AVOID"