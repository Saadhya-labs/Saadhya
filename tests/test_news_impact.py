from app.news.news_enriched_scanner import NewsEnrichedScanner
from app.news.news_impact import NewsImpactEngine


def test_news_impact_labels_positive_and_negative_headlines():
    engine = NewsImpactEngine()

    positive = engine.analyze([{"title": "Company wins record contract and reports profit"}])
    negative = engine.analyze([{"title": "Company reports loss after fraud probe and penalty"}])

    assert positive["impact"] == "POSITIVE"
    assert negative["impact"] == "NEGATIVE"


def test_news_enriched_scanner_preserves_technical_score():
    class Scanner:
        reports = []

        def scan(self):
            return [{"symbol": "HAL.NS", "score": 80}]

    class Provider:
        def headlines(self, symbol):
            return [{"title": "HAL wins contract"}]

    result = NewsEnrichedScanner(Scanner(), Provider(), NewsImpactEngine()).scan()[0]

    assert result["score"] == 80
    assert result["news_impact"]["impact"] == "POSITIVE"
