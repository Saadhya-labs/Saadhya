from app.analyzer.analyzer import StockAnalyzer
from app.ranking.opportunity_score import OpportunityScore


analyzer = StockAnalyzer()

report = analyzer.analyze("HAL.NS")

engine = OpportunityScore()

score = engine.calculate(report)


print("=" * 50)
print(report.symbol)
print("=" * 50)

print()
print("Recommendation:")
print(report.recommendation)

print()
print("Confidence:")
print(report.confidence)

print()
print("Opportunity Score:")
print(score)

print()
print("Signals:")

for key, value in report.signals.items():
    print(f"{key:<15}{value}")