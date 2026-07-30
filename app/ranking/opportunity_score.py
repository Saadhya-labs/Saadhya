class OpportunityScore:

    def calculate(
        self,
        signals,
        recommendation=None
    ):

        if recommendation is None:

            report = signals

            signals = report.signals

            recommendation = {
                "risk": report.risk,
                "confidence": report.confidence
            }

        breakdown = {}

        # -------------------------
        # Trend (25)
        # -------------------------

        trend = 0

        if signals.get("EMA") == "BUY":
            trend += 12

        if signals.get("SUPERTREND") == "BUY":
            trend += 13

        breakdown["trend"] = trend

        # -------------------------
        # Momentum (20)
        # -------------------------

        momentum = 0

        if signals.get("MACD") == "BUY":
            momentum += 15

        if signals.get("RSI") == "BUY":
            momentum += 5

        elif signals.get("RSI") == "HOLD":
            momentum += 3

        breakdown["momentum"] = momentum

        # -------------------------
        # Indicator Agreement (20)
        # -------------------------

        bullish = 0
        bearish = 0

        for signal in signals.values():

            if signal == "BUY":
                bullish += 1

            elif signal == "SELL":
                bearish += 1

        agreement = max(
            bullish,
            bearish
        ) * 5

        breakdown["agreement"] = min(
            agreement,
            20
        )

        # -------------------------
        # Risk (10)
        # -------------------------

        risk = 0

        if recommendation["risk"] == "LOW":
            risk = 10

        elif recommendation["risk"] == "MEDIUM":
            risk = 5

        breakdown["risk"] = risk

        # -------------------------
        # Confidence (25)
        # -------------------------

        confidence = min(

            int(
                recommendation["confidence"] * 0.25
            ),

            25

        )

        breakdown["confidence"] = confidence

        total = sum(

            breakdown.values()

        )

        return {

            "total": min(
                total,
                100
            ),

            "breakdown": breakdown

        }