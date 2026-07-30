from app.models.analysis_report import AnalysisReport
from app.data.market_data import MarketData
from app.indicators.ema import EMAIndicator
from app.indicators.rsi import RSIIndicator
from app.indicators.macd import MACDIndicator
from app.indicators.vwap import VWAPIndicator
from app.indicators.supertrend import SuperTrendIndicator
from app.strategy.recommendation_engine import RecommendationEngine


class StockAnalyzer:

    def __init__(self):
        self.market = MarketData()

        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.macd = MACDIndicator()
        self.vwap = VWAPIndicator()
        self.supertrend = SuperTrendIndicator()

        self.recommendation_engine = RecommendationEngine()

    def analyze(self, symbol):

        # Download historical data
        df = self.market.get_history(symbol)

        if df.empty:
            return None

        # Calculate indicators
        df = self.ema.calculate(df)
        df = self.rsi.calculate(df)
        df = self.macd.calculate(df)
        df = self.vwap.calculate(df)
        df = self.supertrend.calculate(df)

        latest = df.iloc[-1]

        price = latest["Close"]

        # Generate signals
        signals = {
            "EMA": self.ema.signal(latest),
            "RSI": self.rsi.signal(latest["RSI"]),
            "MACD": self.macd.signal(latest),
            "VWAP": self.vwap.signal(latest),
            "SUPERTREND": self.supertrend.signal(latest),
        }

        rec = self.recommendation_engine.generate(signals)

        return AnalysisReport(
    symbol=symbol,
    price=float(price),
    signals=signals,
    recommendation=rec["recommendation"],
    confidence=rec["confidence"],
    direction=rec["direction"],
    opportunity_score=rec["confidence"],
    risk=rec["risk"],
    holding=rec["holding"],
    simple_reasons=rec["simple_reasons"],
    technical_reasons=rec["technical_reasons"],
    suggested_action=(
        "Consider buying gradually"
        if rec["direction"] == "BUY"
        else "Avoid or wait for improvement"
    ),
    invalidation=[
        "Trend reversal",
        "Loss of momentum",
        "Price moves below support"
    ]
)