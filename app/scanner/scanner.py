from app.analyzer.analyzer import StockAnalyzer
from app.scanner.universe import NSE_STOCKS


class StockScanner:

    def __init__(self, analyzer=None, symbols=None):
        self.analyzer = analyzer or StockAnalyzer()
        self.symbols = symbols or NSE_STOCKS
        self.failures = []

    def scan(self):

        results = []

        self.failures = []

        for symbol in self.symbols:

            try:
                result = self.analyzer.analyze(symbol)

                if result is not None:
                    results.append(result)

            except (ValueError, KeyError, TypeError) as exc:
                self.failures.append({"symbol": symbol, "error": str(exc)})

        # Sort by confidence (highest first)
        results.sort(
            key=lambda x: x.confidence,
            reverse=True
        )

        return results
