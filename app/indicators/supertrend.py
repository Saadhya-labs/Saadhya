import pandas as pd
import pandas_ta as ta


class SuperTrendIndicator:
    def __init__(self, length=10, multiplier=3):
        self.length = length
        self.multiplier = multiplier

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        st = ta.supertrend(
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            length=self.length,
            multiplier=self.multiplier
        )

        # Get the actual column names returned by pandas_ta
        data["SUPERT"] = st.iloc[:, 0]
        data["SUPERT_DIRECTION"] = st.iloc[:, 1]

        return data

    def signal(self, row):
        if row["Close"] > row["SUPERT"]:
            return "BUY"

        elif row["Close"] < row["SUPERT"]:
            return "SELL"

        return "HOLD"