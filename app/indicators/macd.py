import pandas as pd



class MACDIndicator:


    def __init__(
        self,
        fast=12,
        slow=26,
        signal_period=9
    ):

        self.fast = fast

        self.slow = slow

        self.signal_period = signal_period



    def calculate(
        self,
        data
    ):


        df = data.copy()


        close = df["Close"]


        fast_ema = (
            close
            .ewm(
                span=self.fast,
                adjust=False
            )
            .mean()
        )


        slow_ema = (
            close
            .ewm(
                span=self.slow,
                adjust=False
            )
            .mean()
        )


        macd_line = fast_ema - slow_ema


        signal_line = (
            macd_line
            .ewm(
                span=self.signal_period,
                adjust=False
            )
            .mean()
        )


        histogram = macd_line - signal_line


        df["MACD"] = macd_line

        df["MACD_SIGNAL"] = signal_line

        df["MACD_HIST"] = histogram


        return df