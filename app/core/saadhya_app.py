from app.analyzer.analyzer import StockAnalyzer
from app.config.settings import Settings
from app.reports.recommendation_report import RecommendationReport


class SaadhyaApp:
    """Recommendation-only application facade."""

    def __init__(self, analyzer=None, report_engine=None):
        self.settings = Settings
        self.analyzer = analyzer or StockAnalyzer()
        self.report_engine = report_engine or RecommendationReport(
            limit=self.settings.SCAN_LIMIT
        )



    def analyze(
        self,
        symbol=None
    ):

        if symbol is None:

            symbol = self.settings.DEFAULT_SYMBOL


        return self.analyzer.analyze(
            symbol
        )



    def generate_report(self, opportunities, metadata=None):

        return self.report_engine.generate(
            opportunities,
            metadata=metadata
        )
