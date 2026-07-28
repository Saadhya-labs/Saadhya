import pandas as pd
import pandas_ta as ta


class RSIIndicator:
    def __init__(self, length=14):
        self.length = length

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Adds RSI column to DataFrame.
        """
        data = data.copy()
        data["RSI"] = ta.rsi(data["Close"], length=self.length)
        return data

    def signal(self, rsi_value: float) -> str:
        """
        Returns trading signal based on RSI.
        """
        if rsi_value > 70:
            return "SELL"

        elif rsi_value < 30:
            return "BUY"

        return "HOLD"