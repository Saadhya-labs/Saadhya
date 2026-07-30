from app.scanner.ranked_scanner import RankedScanner


symbols = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "BEL.NS",
    "HAL.NS"
]


scanner = RankedScanner()

results = scanner.scan(symbols)


print()
print("=" * 70)
print("              SAADHYA MARKET SCAN")
print("=" * 70)


for item in results:

    report = item["report"]

    print()
    print(
        f"{report.symbol:<15}"
        f"{report.recommendation:<15}"
        f"Score: {item['score']}/100"
    )