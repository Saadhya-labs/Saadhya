"""Walk-forward evaluation for recommendation quality.

This evaluator observes historical outcomes only. It never creates orders,
positions, or simulated executions.
"""


class RecommendationEvaluator:
    def __init__(self, signal_engine, recommendation_engine, lookback=30, horizon=5):
        if lookback < 2 or horizon < 1:
            raise ValueError("lookback must be at least 2 and horizon must be positive")
        self.signal_engine = signal_engine
        self.recommendation_engine = recommendation_engine
        self.lookback = lookback
        self.horizon = horizon

    def evaluate(self, data):
        required = {"Close"}
        if not required.issubset(data.columns):
            raise ValueError("Historical data must include Close")

        observations = []
        last_start = len(data) - self.horizon
        for end in range(self.lookback, last_start + 1):
            recommendation = self.recommendation_engine.generate(
                self.signal_engine.generate(data.iloc[:end])
            )
            direction = recommendation["direction"]
            if direction not in {"BUY", "SELL"}:
                continue

            entry = float(data.iloc[end - 1]["Close"])
            exit_price = float(data.iloc[end + self.horizon - 1]["Close"])
            raw_return = (exit_price - entry) / entry * 100
            directional_return = raw_return if direction == "BUY" else -raw_return
            observations.append(
                {
                    "direction": direction,
                    "confidence": recommendation["confidence"],
                    "return_pct": round(directional_return, 4),
                    "correct": directional_return > 0,
                }
            )

        total = len(observations)
        wins = sum(item["correct"] for item in observations)
        average_return = sum(item["return_pct"] for item in observations) / total if total else 0
        return {
            "observations": observations,
            "trades_evaluated": total,
            "wins": wins,
            "hit_rate": round(wins / total * 100, 2) if total else 0,
            "average_directional_return_pct": round(average_return, 4),
            "lookback": self.lookback,
            "horizon": self.horizon,
        }
