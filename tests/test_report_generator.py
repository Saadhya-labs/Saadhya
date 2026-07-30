from app.scanner.ranked_scanner import RankedScanner
from app.scanner.report_generator import ReportGenerator


symbols = [
    "HAL.NS",
    "TCS.NS",
    "INFY.NS"
]


scanner = RankedScanner()

results = scanner.scan(symbols)


generator = ReportGenerator()

reports = generator.generate(results)


print()
print("=" * 60)
print("SAADHYA OPPORTUNITY REPORT")
print("=" * 60)


for item in reports:

    print()
    print(item["symbol"])
    print("Score:", item["score"])
    print("Recommendation:", item["recommendation"])
    print("Action:", item["decision"]["action"])
    print("Entry:", item["decision"].get("entry"))
    print("Target:", item["decision"].get("target"))
    print("Stop:", item["decision"].get("stop_loss"))