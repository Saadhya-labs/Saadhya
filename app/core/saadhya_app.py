from app.config.settings import Settings
from app.broker.broker_factory import BrokerFactory
from app.analyzer.analyzer import StockAnalyzer


class SaadhyaApp:

    def __init__(self):

        self.settings = Settings()

        self.broker = BrokerFactory.create(
            self.settings.BROKER
        )

        self.analyzer = StockAnalyzer()


    def analyze(
        self,
        symbol=None
    ):

        if symbol is None:

            symbol = self.settings.DEFAULT_SYMBOL


        return self.analyzer.analyze(
            symbol
        )


    def place_trade(
        self,
        symbol,
        direction,
        quantity,
        price
    ):

        order = self.broker.place_order(

            symbol=symbol,

            direction=direction,

            quantity=quantity,

            price=price

        )

        return order