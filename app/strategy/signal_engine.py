from typing import Dict


class SignalEngine:
    def generate(self, signals: Dict[str, str]) -> dict:
        """
        Combines indicator signals into one recommendation.
        """

        score = 0

        for signal in signals.values():
            if signal == "BUY":
                score += 1

            elif signal == "SELL":
                score -= 1

        total = len(signals)

        confidence = round((abs(score) / total) * 100)

        if score >= 4:
            recommendation = "STRONG BUY"

        elif score >= 2:
            recommendation = "BUY"

        elif score <= -4:
            recommendation = "STRONG SELL"

        elif score <= -2:
            recommendation = "SELL"

        else:
            recommendation = "HOLD"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "score": score
        }