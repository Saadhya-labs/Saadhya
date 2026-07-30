from app.models.analysis_report import AnalysisReport


class AnalysisReportBuilder:
    """Builds stock-analysis reports from already computed results."""

    def build(self, symbol, price, signals, recommendation, opportunity_score):
        return AnalysisReport(
            symbol=symbol,
            price=float(price),
            signals=signals,
            recommendation=recommendation["recommendation"],
            confidence=recommendation["confidence"],
            direction=recommendation["direction"],
            opportunity_score=opportunity_score,
            risk=recommendation.get("risk", "MEDIUM"),
            holding=recommendation.get("holding", "Swing"),
            simple_reasons=recommendation.get("simple_reasons", []),
            technical_reasons=recommendation.get("technical_reasons", []),
            suggested_action=recommendation.get("suggested_action", ""),
            invalidation=recommendation.get("invalidation", []),
        )
