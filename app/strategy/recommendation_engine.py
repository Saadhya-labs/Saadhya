class RecommendationEngine:

    def __init__(self):
        pass

    def generate(self, signals):

        score = 0
        reasons = []
        simple_reasons = []

        # EMA
        if signals["EMA"] == "BUY":
            score += 20
            reasons.append("EMA Bullish")
            simple_reasons.append(
                "The short-term trend is stronger than the long-term trend."
            )
        elif signals["EMA"] == "SELL":
            score -= 20
            reasons.append("EMA Bearish")
            simple_reasons.append(
                "The recent trend is weaker than the long-term trend."
            )

        # RSI
        if signals["RSI"] == "BUY":
            score += 10
            reasons.append("RSI Oversold")
            simple_reasons.append(
                "The stock may be recovering after being oversold."
            )
        elif signals["RSI"] == "SELL":
            score -= 10
            reasons.append("RSI Overbought")
            simple_reasons.append(
                "The stock has risen quickly and may slow down."
            )

        # MACD
        if signals["MACD"] == "BUY":
            score += 20
            reasons.append("MACD Bullish")
            simple_reasons.append(
                "Buying momentum is increasing."
            )
        elif signals["MACD"] == "SELL":
            score -= 20
            reasons.append("MACD Bearish")
            simple_reasons.append(
                "Selling pressure is increasing."
            )

        # VWAP
        if signals["VWAP"] == "BUY":
            score += 15
            reasons.append("Above VWAP")
            simple_reasons.append(
                "The stock is trading above its average traded price."
            )
        elif signals["VWAP"] == "SELL":
            score -= 15
            reasons.append("Below VWAP")
            simple_reasons.append(
                "The stock is trading below its average traded price."
            )

        # SuperTrend
        if signals["SUPERTREND"] == "BUY":
            score += 20
            reasons.append("SuperTrend Bullish")
            simple_reasons.append(
                "The overall trend is still moving upward."
            )
        elif signals["SUPERTREND"] == "SELL":
            score -= 20
            reasons.append("SuperTrend Bearish")
            simple_reasons.append(
                "The overall trend is moving downward."
            )

        confidence = abs(score)

        if score >= 60:
            recommendation = "STRONG BUY"
            direction = "BUY"
            risk = "LOW"
            holding = "Swing (5-10 days)"

        elif score >= 20:
            recommendation = "BUY"
            direction = "BUY"
            risk = "MEDIUM"
            holding = "Swing (3-7 days)"

        elif score <= -60:
            recommendation = "STRONG SELL"
            direction = "SELL"
            risk = "LOW"
            holding = "Avoid / Exit"

        elif score <= -20:
            recommendation = "SELL"
            direction = "SELL"
            risk = "MEDIUM"
            holding = "Short-term Weakness"

        else:
            recommendation = "HOLD"
            direction = "WATCH"
            risk = "MEDIUM"
            holding = "Wait"

        return {
            "recommendation": recommendation,
            "direction": direction,
            "confidence": confidence,
            "score": score,
            "risk": risk,
            "holding": holding,
            "technical_reasons": reasons,
            "simple_reasons": simple_reasons,
        }