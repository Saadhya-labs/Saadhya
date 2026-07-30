from app.strategy.trade_decision import TradeDecision


class ReportGenerator:

    def __init__(self):
        self.decision_engine = TradeDecision()


    def generate(self, ranked_results):

        reports = []

        for item in ranked_results:

            report = item["report"]

            decision = self.decision_engine.calculate(report)


            reports.append(
                {
                    "symbol": report.symbol,
                    "score": item["score"],
                    "recommendation": report.recommendation,
                    "confidence": report.confidence,
                    "decision": decision,
                    "signals": report.signals
                }
            )


        return reports