"""Explainable, deliberately conservative news-context classifier."""


class NewsImpactEngine:
    POSITIVE_WORDS = {
        "beat", "bullish", "buyback", "contract", "growth", "profit", "record",
        "upgrade", "wins", "surge", "approval", "dividend",
    }
    NEGATIVE_WORDS = {
        "bearish", "downgrade", "fall", "fraud", "loss", "probe", "risk",
        "slump", "weak", "warning", "decline", "penalty",
    }

    def analyze(self, articles):
        score = 0
        matched_positive = []
        matched_negative = []
        for article in articles:
            words = set(article.get("title", "").lower().replace("-", " ").split())
            positive = sorted(words & self.POSITIVE_WORDS)
            negative = sorted(words & self.NEGATIVE_WORDS)
            score += len(positive) - len(negative)
            matched_positive.extend(positive)
            matched_negative.extend(negative)

        if score >= 2:
            impact = "POSITIVE"
        elif score <= -2:
            impact = "NEGATIVE"
        else:
            impact = "NEUTRAL"
        return {
            "impact": impact,
            "score": score,
            "headlines": articles[:3],
            "matched_positive": sorted(set(matched_positive)),
            "matched_negative": sorted(set(matched_negative)),
            "warning": "News impact is keyword-based context, not a forecast.",
        }
