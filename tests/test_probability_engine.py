from app.strategy.probability_engine import ProbabilityEngine



engine = ProbabilityEngine()


result = engine.calculate(

    option_score=90,

    market_regime="BULLISH"

)


print("="*60)

print(
    "SAADHYA PROBABILITY"
)

print("="*60)


print(
    result
)