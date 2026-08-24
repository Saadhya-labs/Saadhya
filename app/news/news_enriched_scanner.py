class NewsEnrichedScanner:
    """Adds news context to scanner results without changing technical scores."""

    def __init__(self, scanner, news_provider, impact_engine):
        self._scanner = scanner
        self.news_provider = news_provider
        self.impact_engine = impact_engine
        self.failures = []

    @property
    def reports(self):
        return self._scanner.reports

    def scan(self):
        results = self._scanner.scan()
        self.failures = []
        enriched = []
        for item in results:
            result = item.copy()
            try:
                news = self.impact_engine.analyze(self.news_provider.headlines(item["symbol"]))
                result["news_impact"] = news
                result["warnings"] = [news["warning"]]
            except Exception as exc:
                result["news_impact"] = {"impact": "UNAVAILABLE", "headlines": []}
                result["warnings"] = ["News context is unavailable."]
                self.failures.append({"symbol": item["symbol"], "source": "news", "error": str(exc)})
            enriched.append(result)
        return enriched
