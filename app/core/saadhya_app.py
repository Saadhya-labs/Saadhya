from app.config.settings import Settings
from app.broker.broker_factory import BrokerFactory
from app.analyzer.analyzer import StockAnalyzer
from app.reports.recommendation_report import RecommendationReport


class SaadhyaApp:


    def __init__(self):

        self.settings = Settings

        self.broker = BrokerFactory.create(
            self.settings.BROKER
        )

        self.analyzer = StockAnalyzer()

        self.report_engine = RecommendationReport()



    def analyze(
        self,
        symbol=None
    ):

        if symbol is None:

            symbol = self.settings.DEFAULT_SYMBOL


        return self.analyzer.analyze(
            symbol
        )



    def generate_report(
        self,
        opportunities
    ):

        return self.report_engine.generate(
            opportunities
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