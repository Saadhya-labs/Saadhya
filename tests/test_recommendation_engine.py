from app.strategy.recommendation_engine import RecommendationEngine

signals = {
    "EMA": "BUY",
    "RSI": "HOLD",
    "MACD": "BUY",
    "VWAP": "BUY",
    "SUPERTREND": "BUY",
}

engine = RecommendationEngine()

result = engine.generate(signals)

print()

print("Recommendation :", result["recommendation"])
print("Confidence     :", result["confidence"])
print("Score          :", result["score"])

print()

print("Reasons")

for reason in result["reasons"]:
    print("-", reason)