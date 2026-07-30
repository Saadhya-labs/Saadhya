import yfinance as yf
import pandas as pd


class MarketData:
    def get_history(self, symbol: str, period="6mo", interval="1d") -> pd.DataFrame:

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False
        )

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        return df