from app.analyzer.analyzer import StockAnalyzer

analyzer = StockAnalyzer()

result = analyzer.analyze("RELIANCE.NS")

print()

print("=" * 50)
print(result["symbol"])
print("=" * 50)

print(f"Price : {result['price']:.2f}")

print()

print("Signals")

for indicator, signal in result["signals"].items():
    print(f"{indicator:15} {signal}")

print()

print("Recommendation")

print(result["recommendation"]["recommendation"])

print("Confidence")

print(result["recommendation"]["confidence"])
rec = result["recommendation"]

print()
print("=" * 60)
print(result["symbol"])
print("=" * 60)

print(f"Price        : {result['price']:.2f}")
print(f"Recommendation: {rec['recommendation']}")
print(f"Confidence   : {rec['confidence']}%")
print(f"Risk         : {rec['risk']}")
print(f"Holding      : {rec['holding']}")

print("\nSignals")
for k, v in result["signals"].items():
    print(f"{k:15} {v}")

print("\nWhy? (Simple)")
for reason in rec["simple_reasons"]:
    print(f"• {reason}")

print("\nTechnical Reasons")
for reason in rec["technical_reasons"]:
    print(f"• {reason}")