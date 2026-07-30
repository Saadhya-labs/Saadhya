from app.scanner.scanner import StockScanner

scanner = StockScanner()

results = scanner.scan()

print()
print("=" * 75)
print("TODAY'S MARKET SCAN")
print("=" * 75)

for stock in results:

    rec = stock["recommendation"]

    print(
        f"{stock['symbol']:18}"
        f"{rec['recommendation']:15}"
        f"{rec['confidence']}%"
    )