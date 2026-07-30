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

        self.engine = RecommendationEngine()

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

        # Generate signals
        signals = {
            "EMA": self.ema.signal(latest),
            "RSI": self.rsi.signal(latest["RSI"]),
            "MACD": self.macd.signal(latest),
            "VWAP": self.vwap.signal(latest),
            "SUPERTREND": self.supertrend.signal(latest),
        }

        recommendation = self.engine.generate(signals)

        return {
            "symbol": symbol,
            "price": float(latest["Close"]),
            "signals": signals,
            "recommendation": recommendation,
        }