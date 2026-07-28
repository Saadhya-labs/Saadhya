import pandas as pd


class EMAIndicator:
    """
    Calculates Exponential Moving Averages and detects crossovers.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def calculate(self, short_period=9, long_period=21):
        self.data["EMA_Short"] = (
            self.data["Close"].ewm(span=short_period, adjust=False).mean()
        )

        self.data["EMA_Long"] = (
            self.data["Close"].ewm(span=long_period, adjust=False).mean()
        )

        return self.data

    def signal(self):
        latest = self.data.iloc[-1]

        if latest["EMA_Short"] > latest["EMA_Long"]:
            return "BULLISH"

        if latest["EMA_Short"] < latest["EMA_Long"]:
            return "BEARISH"

        return "NEUTRAL"