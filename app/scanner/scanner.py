from app.analyzer.analyzer import StockAnalyzer
from app.scanner.universe import NSE_STOCKS


class StockScanner:

    def __init__(self):
        self.analyzer = StockAnalyzer()

    def scan(self):

        results = []

        print("\nScanning market...\n")

        for symbol in NSE_STOCKS:

            try:
                print(f"Analyzing {symbol}")

                result = self.analyzer.analyze(symbol)

                if result is not None:
                    results.append(result)

            except Exception as e:
                print(f"{symbol}: {e}")

        # Sort by confidence (highest first)
        results.sort(
            key=lambda x: x["recommendation"]["confidence"],
            reverse=True
        )

        return results