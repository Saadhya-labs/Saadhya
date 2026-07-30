from app.strategy.signal_engine import SignalEngine
from app.strategy.recommendation_engine import RecommendationEngine
from app.ranking.opportunity_score import OpportunityScore
from app.models.analysis_report import AnalysisReport



class StockAnalyzer:



    def __init__(
        self,
        stock_provider
    ):


        self.stock_provider = stock_provider

        self.signal_engine = SignalEngine()

        self.recommendation_engine = RecommendationEngine()

        self.opportunity_score = OpportunityScore()



    def analyze(
        self,
        symbol
    ):


        df = self.stock_provider.get_history(
            symbol
        )


        price = self.stock_provider.get_price(
            symbol
        )


        signals = self.signal_engine.generate(
            df
        )


        recommendation = self.recommendation_engine.generate(
            signals
        )


        report = AnalysisReport(

            symbol=symbol,

            price=price,

            signals=signals,

            recommendation=recommendation["recommendation"],

            confidence=recommendation["confidence"],

            direction=recommendation["direction"],

            opportunity_score=0,

            risk=recommendation.get(
                "risk",
                "MEDIUM"
            ),

            holding=recommendation.get(
                "holding",
                "Swing"
            ),

            simple_reasons=recommendation.get(
                "simple_reasons",
                []
            ),

            technical_reasons=recommendation.get(
                "technical_reasons",
                []
            ),

            suggested_action=recommendation.get(
                "suggested_action",
                ""
            ),

            invalidation=recommendation.get(
                "invalidation",
                []
            )

        )


        score = self.opportunity_score.calculate(
            report
        )


        report.opportunity_score = score


        return report