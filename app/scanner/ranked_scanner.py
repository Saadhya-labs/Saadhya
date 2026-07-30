from app.analyzer.analyzer import StockAnalyzer
from app.ranking.opportunity_score import OpportunityScore


class RankedScanner:

    def __init__(self):
        self.analyzer = StockAnalyzer()
        self.score_engine = OpportunityScore()


    def scan(self, symbols):

        results = []

        print()
        print("Scanning market...")
        print()

        for symbol in symbols:

            try:
                print(f"Analyzing {symbol}")

                report = self.analyzer.analyze(symbol)

                score = self.score_engine.calculate(report)


                results.append(
                    {
                        "symbol": symbol,
                        "report": report,
                        "score": score["total"],
                        "breakdown": score["breakdown"]
                    }
                )


            except Exception as e:

                print(
                    f"Skipping {symbol}: {e}"
                )


        # Highest opportunity first

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )


        return results