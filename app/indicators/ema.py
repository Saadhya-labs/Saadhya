import pandas as pd


class EMAIndicator:
    def __init__(self, short_period=9, long_period=21):
        self.short_period = short_period
        self.long_period = long_period

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        data["EMA_Short"] = data["Close"].ewm(
            span=self.short_period,
            adjust=False
        ).mean()

        data["EMA_Long"] = data["Close"].ewm(
            span=self.long_period,
            adjust=False
        ).mean()

        return data

    def signal(self, row):
        if row["EMA_Short"] > row["EMA_Long"]:
            return "BUY"

        elif row["EMA_Short"] < row["EMA_Long"]:
            return "SELL"

        return "HOLD"