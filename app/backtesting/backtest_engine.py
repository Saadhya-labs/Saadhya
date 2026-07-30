from app.portfolio.paper_trading_engine import PaperTradingEngine
from app.portfolio.trade_journal import TradeJournal


class BacktestEngine:

    def __init__(

        self,

        analyzer,

        risk_manager,

        provider

    ):

        self.analyzer = analyzer

        self.risk_manager = risk_manager

        self.provider = provider

        self.engine = PaperTradingEngine()

        self.journal = TradeJournal()


    def run(

        self,

        symbol

    ):

        report = self.analyzer.analyze(

            symbol

        )

        return report