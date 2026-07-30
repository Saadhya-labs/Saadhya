from abc import ABC, abstractmethod



class StockDataProvider(ABC):


    @abstractmethod
    def get_history(
        self,
        symbol,
        period="6mo"
    ):

        pass



    @abstractmethod
    def get_price(
        self,
        symbol
    ):

        pass