from typing import Dict


class RecommendationEngine:
    WEIGHTS = {
        "EMA": 20,
        "RSI": 10,
        "MACD": 25,
        "VWAP": 15,
        "SUPERTREND": 30,
    }

    def generate(self, signals: Dict[str, str]) -> dict:
        score = 0
        max_score = sum(self.WEIGHTS.values())

        reasons = []

        for indicator, signal in signals.items():
            weight = self.WEIGHTS.get(indicator, 0)

            if signal == "BUY":
                score += weight
                reasons.append(f"{indicator} Bullish")

            elif signal == "SELL":
                score -= weight
                reasons.append(f"{indicator} Bearish")

        confidence = round(abs(score) / max_score * 100)

        if score >= 70:
            recommendation = "STRONG BUY"

        elif score >= 30:
            recommendation = "BUY"

        elif score <= -70:
            recommendation = "STRONG SELL"

        elif score <= -30:
            recommendation = "SELL"

        else:
            recommendation = "HOLD"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "score": score,
            "reasons": reasons,
        }