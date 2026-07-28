import pandas as pd


class VWAPIndicator:
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        typical_price = (
            data["High"] +
            data["Low"] +
            data["Close"]
        ) / 3

        cumulative_tp_volume = (typical_price * data["Volume"]).cumsum()
        cumulative_volume = data["Volume"].cumsum()

        data["VWAP"] = cumulative_tp_volume / cumulative_volume

        return data

    def signal(self, row):
        if row["Close"] > row["VWAP"]:
            return "BUY"

        elif row["Close"] < row["VWAP"]:
            return "SELL"

        return "HOLD"