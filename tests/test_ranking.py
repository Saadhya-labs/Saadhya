from app.analyzer.analyzer import StockAnalyzer
from app.ranking.opportunity_score import OpportunityScore


def test_opportunity_score_generation():

    analyzer = StockAnalyzer()

    report = analyzer.analyze(
        "HAL.NS"
    )

    engine = OpportunityScore()

    score = engine.calculate(
        report
    )

    assert report.symbol == "HAL.NS"

    assert report.recommendation

    assert report.confidence >= 0

    assert score["total"] <= 100

    assert "breakdown" in score

    assert set(score["breakdown"]) == {
        "trend",
        "momentum",
        "agreement",
        "risk",
        "confidence",
    }