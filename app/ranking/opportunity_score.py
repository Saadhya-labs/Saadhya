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
                "direction": report.direction,
                "risk": report.risk,
                "confidence": report.confidence
            }

        direction = recommendation.get("direction", "WATCH")
        expected_signal = direction if direction in {"BUY", "SELL"} else None

        def aligned(signal_name):
            return expected_signal is not None and signals.get(signal_name) == expected_signal

        breakdown = {}

        # -------------------------
        # Trend (25)
        # -------------------------

        trend = 0

        if aligned("EMA"):
            trend += 12

        if aligned("SUPERTREND"):
            trend += 13

        breakdown["trend"] = trend

        # -------------------------
        # Momentum (20)
        # -------------------------

        momentum = 0

        if aligned("MACD"):
            momentum += 15

        if aligned("RSI"):
            momentum += 5

        elif expected_signal is None and signals.get("RSI") == "HOLD":
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

        agreement = (
            (bullish if expected_signal == "BUY" else bearish)
            if expected_signal is not None
            else 0
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
