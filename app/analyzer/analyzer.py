from app.analyzer.analysis_report_builder import AnalysisReportBuilder
from app.config.provider_factory import get_stock_provider
from app.ranking.opportunity_score import OpportunityScore
from app.strategy.recommendation_engine import RecommendationEngine
from app.strategy.signal_engine import SignalEngine


class StockAnalyzer:
    """Coordinates the stock-analysis pipeline without option concerns."""

    def __init__(self, provider=None, report_builder=None):

        if provider is None:
            provider = get_stock_provider()

        self.provider = provider
        self.signal_engine = SignalEngine()
        self.recommendation_engine = RecommendationEngine()
        self.opportunity_score = OpportunityScore()
        self.report_builder = report_builder or AnalysisReportBuilder()

    def analyze(self, symbol):
        data = self.provider.get_history(symbol)
        name_lookup = getattr(self.provider, "get_company_name", None)
        company_name = ""
        if callable(name_lookup):
            try:
                company_name = name_lookup(symbol)
            except (KeyError, TypeError, ValueError, RuntimeError):
                # A display label must not suppress an otherwise usable
                # cached recommendation while the instrument master reconnects.
                company_name = ""
        return self.analyze_dataframe(data, symbol, company_name=company_name)

    def analyze_dataframe(self, data, symbol, company_name=""):

        signals = self.signal_engine.generate(data)

        recommendation = self.recommendation_engine.generate(
            signals
        )

        opportunity_score = self.opportunity_score.calculate(
            signals,
            recommendation
        )

        return self.report_builder.build(
            symbol=symbol,
            price=data.iloc[-1]["Close"],
            signals=signals,
            recommendation=recommendation,
            opportunity_score=opportunity_score,
            company_name=company_name,
        )
