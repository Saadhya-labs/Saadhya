import pandas as pd

from app.backtesting.recommendation_evaluator import RecommendationEvaluator


class AlwaysBuySignals:
    def generate(self, data):
        return {"signal": "BUY"}


class AlwaysBuyRecommendation:
    def generate(self, signals):
        return {"direction": "BUY", "confidence": 80}


def test_walk_forward_evaluation_reports_observed_outcomes():
    data = pd.DataFrame({"Close": list(range(100, 141))})
    result = RecommendationEvaluator(
        AlwaysBuySignals(), AlwaysBuyRecommendation(), lookback=30, horizon=5
    ).evaluate(data)

    assert result["trades_evaluated"] == 7
    assert result["hit_rate"] == 100
    assert result["average_directional_return_pct"] > 0
