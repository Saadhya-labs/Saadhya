from app.analyzer.analyzer import StockAnalyzer


analyzer = StockAnalyzer()

result = analyzer.analyze("RELIANCE.NS")


print()
print("=" * 50)
print(result.symbol)
print("=" * 50)

print(f"Price : {result.price:.2f}")

print()
print("Signals")

for key, value in result.signals.items():
    print(f"{key:<15} {value}")


print()
print("Recommendation")
print(result.recommendation)

print()
print("Confidence")
print(result.confidence)


print()
print("Risk")
print(result.risk)


print()
print("Holding")
print(result.holding)


print()
print("Opportunity Score")
print(result.opportunity_score)


print()
print("Why? (Simple)")

for reason in result.simple_reasons:
    print(f"• {reason}")


print()
print("Technical Reasons")

for reason in result.technical_reasons:
    print(f"• {reason}")


print()
print("Suggested Action")
print(result.suggested_action)


print()
print("Invalidation Conditions")

for item in result.invalidation:
    print(f"• {item}")