from app.data.providers.stock_provider import StockDataProvider



class NSEStockProvider(StockDataProvider):



    def get_history(
        self,
        symbol,
        period="6mo"
    ):


        raise NotImplementedError(

            "NSE live stock data integration pending"

        )



    def get_price(
        self,
        symbol
    ):


        raise NotImplementedError(

            "NSE live stock price integration pending"

        )