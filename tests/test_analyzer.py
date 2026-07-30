from app.analyzer.analyzer import StockAnalyzer
from app.config.provider_factory import get_stock_provider



print("=" * 60)

print(
    "SAADHYA ANALYZER TEST"
)

print("=" * 60)



provider = get_stock_provider()



print()

print(
    "Provider:",
    type(provider).__name__
)



analyzer = StockAnalyzer(

    provider

)



result = analyzer.analyze(

    "HAL.NS"

)



print()

print(
    "Symbol:",
    result.symbol
)



print(
    "Price:",
    result.price
)



print()

print(
    "Signals"
)



for key, value in result.signals.items():

    print(
        f"{key:<15}",
        value
    )



print()

print(
    "Recommendation:"
)



print(
    result.recommendation
)



print()

print(
    "Confidence:"
)



print(
    result.confidence
)



print()

print(
    "Opportunity Score:"
)



print(
    result.opportunity_score
)



print()

print(
    "Risk:"
)



print(
    result.risk
)