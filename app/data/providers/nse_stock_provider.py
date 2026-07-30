import yfinance as yf

from app.data.providers.stock_provider import StockDataProvider


class NSEStockProvider(StockDataProvider):
    """
    Live market data provider.

    Backend:
    Yahoo Finance via yfinance

    Output contract:
    Open
    High
    Low
    Close
    Volume
    """



    def _normalize(
        self,
        df
    ):

        if df.empty:

            raise ValueError(
                "Empty market data received"
            )


        # Handle yfinance MultiIndex columns

        if hasattr(
            df.columns,
            "levels"
        ):

            df.columns = [

                col[0]

                for col in df.columns

            ]


        required = [

            "Open",
            "High",
            "Low",
            "Close",
            "Volume"

        ]


        df = df[required]


        return df



    def get_history(
        self,
        symbol,
        period="6mo"
    ):


        df = yf.download(

            tickers=symbol,

            period=period,

            auto_adjust=False,

            progress=False

        )


        return self._normalize(
            df
        )



    def get_price(
        self,
        symbol
    ):


        df = self.get_history(

            symbol,

            period="5d"

        )


        price = df["Close"].iloc[-1]


        return float(
            price
        )