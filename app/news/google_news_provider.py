"""Small, dependency-free Google News RSS client with a short in-memory cache."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree


class GoogleNewsRssProvider:
    BASE_URL = "https://news.google.com/rss/search"

    def __init__(self, cache_minutes=5, timeout=10):
        self.cache_minutes = cache_minutes
        self.timeout = timeout
        self._cache = {}

    def headlines(self, symbol):
        key = symbol.upper()
        cached = self._cache.get(key)
        now = datetime.now(timezone.utc)
        if cached and now - cached[0] < timedelta(minutes=self.cache_minutes):
            return cached[1]

        query = urlencode(
            {"q": f"{key.replace('.NS', '')} NSE stock", "hl": "en-IN", "gl": "IN", "ceid": "IN:en"}
        )
        request = Request(
            f"{self.BASE_URL}?{query}",
            headers={"User-Agent": "Saadhya/1.0 market research"},
        )
        with urlopen(request, timeout=self.timeout) as response:
            root = ElementTree.fromstring(response.read())

        articles = []
        for item in root.findall("./channel/item")[:10]:
            articles.append(
                {
                    "title": item.findtext("title", default="").strip(),
                    "published_at": item.findtext("pubDate", default="").strip(),
                    "url": item.findtext("link", default="").strip(),
                }
            )
        self._cache[key] = (now, articles)
        return articles
