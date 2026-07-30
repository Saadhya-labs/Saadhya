from app.strategy.recommendation_engine import RecommendationEngine


def test_recommendation_engine_generates_output():

    signals = {
        "EMA": "BUY",
        "RSI": "HOLD",
        "MACD": "BUY",
        "VWAP": "BUY",
        "SUPERTREND": "BUY",
    }

    engine = RecommendationEngine()

    result = engine.generate(signals)

    assert result["recommendation"] == "STRONG BUY"

    assert result["confidence"] > 0

    assert result["score"] > 0

    assert result["technical_reasons"]

    assert result["simple_reasons"]

    assert result["risk"] == "LOW"

    assert result["direction"] == "BUY"