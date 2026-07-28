import pandas as pd
import pandas_ta as ta


class MACDIndicator:
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        macd = ta.macd(
            data["Close"],
            fast=self.fast,
            slow=self.slow,
            signal=self.signal_period
        )

        data["MACD"] = macd[f"MACD_{self.fast}_{self.slow}_{self.signal_period}"]
        data["MACD_SIGNAL"] = macd[f"MACDs_{self.fast}_{self.slow}_{self.signal_period}"]
        data["MACD_HIST"] = macd[f"MACDh_{self.fast}_{self.slow}_{self.signal_period}"]

        return data

    def signal(self, row):
        if row["MACD"] > row["MACD_SIGNAL"]:
            return "BUY"
        elif row["MACD"] < row["MACD_SIGNAL"]:
            return "SELL"

        return "HOLD"