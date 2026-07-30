class OpportunityScore:

    def calculate(self, report):

        breakdown = {}

        # -------------------------
        # Trend Score (25)
        # -------------------------

        trend = 0

        if report.signals.get("EMA") == "BUY":
            trend += 12

        if report.signals.get("SUPERTREND") == "BUY":
            trend += 13

        breakdown["trend"] = trend


        # -------------------------
        # Momentum Score (20)
        # -------------------------

        momentum = 0

        if report.signals.get("MACD") == "BUY":
            momentum += 15

        if report.signals.get("RSI") == "BUY":
            momentum += 5

        elif report.signals.get("RSI") == "HOLD":
            momentum += 3

        breakdown["momentum"] = momentum


        # -------------------------
        # Indicator Agreement (20)
        # -------------------------

        bullish = 0
        bearish = 0

        for signal in report.signals.values():

            if signal == "BUY":
                bullish += 1

            elif signal == "SELL":
                bearish += 1


        agreement = max(bullish, bearish) * 5

        breakdown["agreement"] = min(agreement, 20)


        # -------------------------
        # Risk Score (10)
        # -------------------------

        if report.risk == "LOW":
            risk = 10

        elif report.risk == "MEDIUM":
            risk = 5

        else:
            risk = 0

        breakdown["risk"] = risk


        # -------------------------
        # Confidence Score (25)
        # -------------------------

        confidence = min(
            int(report.confidence * 0.25),
            25
        )

        breakdown["confidence"] = confidence


        total = sum(breakdown.values())


        return {
            "total": min(total, 100),
            "breakdown": breakdown
        }