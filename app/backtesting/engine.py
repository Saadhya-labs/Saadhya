from app.strategy.trade_decision import TradeDecision
from app.portfolio.paper_trading_engine import PaperTradingEngine
from app.portfolio.trade_journal import TradeJournal
from app.portfolio.performance import PerformanceAnalyzer


class BacktestRunner:


    def __init__(self):

        self.decision_engine = TradeDecision()

        self.paper_engine = PaperTradingEngine()

        self.journal = TradeJournal()



    def execute(self, report, quantity=1):


        decision = self.decision_engine.calculate(
            report
        )


        if decision["action"] == "NO TRADE":

            return None



        entry = report.price


        trade = self.paper_engine.open_trade(

            symbol=report.symbol,

            direction=report.direction,

            quantity=quantity,

            entry_price=entry,

            stop_loss=decision["stop_loss"],

            target=decision["target"]

        )


        self.paper_engine.close_trade(

            trade,

            decision["target"]

        )


        self.journal.record_trade(
            trade
        )


        performance = PerformanceAnalyzer(
            self.journal
        )


        return performance.summary()