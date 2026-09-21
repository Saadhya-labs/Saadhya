from app.analyzer.analyzer import StockAnalyzer
from app.scanner.universe import NSE_STOCKS
from concurrent.futures import ThreadPoolExecutor


class StockScanner:

    def __init__(self, analyzer=None, symbols=None, max_workers=1):
        self.analyzer = analyzer or StockAnalyzer()
        self.symbols = symbols or NSE_STOCKS
        self.failures = []
        self.max_workers = max(1, max_workers)

    def _analyze_safe(self, symbol):
        try:
            return self.analyzer.analyze(symbol), None
        except (ValueError, KeyError, TypeError, RuntimeError) as exc:
            return None, {"symbol": symbol, "error": str(exc)}

    def scan(self):

        results = []

        self.failures = []

        if self.max_workers == 1:
            outcomes = map(self._analyze_safe, self.symbols)
            for result, failure in outcomes:
                if result is not None:
                    results.append(result)
                if failure:
                    self.failures.append(failure)
        else:
            # Small bounded pool overlaps independent historical requests.
            # map retains the original symbol ordering for stable ties.
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                for result, failure in pool.map(self._analyze_safe, self.symbols):
                    if result is not None:
                        results.append(result)
                    if failure:
                        self.failures.append(failure)

        # Sort by confidence (highest first)
        results.sort(
            key=lambda x: x.confidence,
            reverse=True
        )

        return results
