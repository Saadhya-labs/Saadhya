from app.strategy.signal_engine import SignalEngine
from app.portfolio.paper_trading_engine import PaperTradingEngine
from app.portfolio.trade_journal import TradeJournal
from app.portfolio.performance import PerformanceAnalyzer


class HistoricalBacktestRunner:


    def __init__(self, provider):

        self.provider = provider

        self.signal_engine = SignalEngine()

        self.paper_engine = PaperTradingEngine()

        self.journal = TradeJournal()



    def run(

        self,

        symbol,

        period="6mo"

    ):


        data = self.provider.get_history(

            symbol,

            period

        )


        signals = self.signal_engine.generate(
            data
        )


        direction = "BUY"


        if signals.get("MACD") == "SELL":

            direction = "SELL"



        price = float(

            data.iloc[-1]["Close"]

        )


        trade = self.paper_engine.open_trade(

            symbol=symbol,

            direction=direction,

            quantity=1,

            entry_price=price,

            stop_loss=price * 0.95,

            target=price * 1.10

        )


        self.paper_engine.close_trade(

            trade,

            trade.target

        )


        self.journal.record_trade(
            trade
        )


        performance = PerformanceAnalyzer(
            self.journal
        )


        return performance.summary()