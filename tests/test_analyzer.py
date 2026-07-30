from app.analyzer.analyzer import StockAnalyzer
from app.data.providers.mock_stock_provider import MockStockProvider



print("=" * 60)

print(
    "SAADHYA ANALYZER TEST"
)

print("=" * 60)



provider = MockStockProvider()



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