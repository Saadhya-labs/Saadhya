from app.analyzer.analyzer import StockAnalyzer
from app.strategy.trade_decision import TradeDecision


analyzer = StockAnalyzer()

report = analyzer.analyze("HAL.NS")


engine = TradeDecision()

decision = engine.calculate(report)


print("=" * 50)

print(report.symbol)

print("=" * 50)

print()

print("Recommendation:")
print(report.recommendation)

print()

print("Decision:")
print(decision)