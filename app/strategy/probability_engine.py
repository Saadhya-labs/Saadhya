class ProbabilityEngine:


    def calculate(
        self,
        option_score,
        market_regime
    ):


        probability = 50

        factors = []

        warnings = []


        # Option quality

        if option_score >= 90:

            probability += 15

            factors.append(
                "Option quality is excellent"
            )


        elif option_score >= 75:

            probability += 10

            factors.append(
                "Option quality is good"
            )


        else:

            warnings.append(
                "Option quality is weak"
            )



        # Market regime

        if market_regime in {"BULLISH", "RISK_ON"}:

            probability += 10

            factors.append(
                "Market trend supports buying"
            )


        elif market_regime in {"BEARISH", "RISK_OFF"}:

            probability -= 10

            warnings.append(
                "Market trend is against trade"
            )



        probability = max(
            0,
            min(
                probability,
                95
            )
        )


        if probability >= 75:

            confidence = "HIGH"

        elif probability >= 60:

            confidence = "MEDIUM"

        else:

            confidence = "LOW"



        return {

            "probability": probability,

            "confidence": confidence,

            "factors": factors,

            "warnings": warnings + [
                "Probability is a heuristic quality score, not a forecast."
            ]

        }
