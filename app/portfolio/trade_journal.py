from app.portfolio.trade import Trade


class TradeJournal:

    def __init__(self):

        self.trades = []

    def record_trade(

        self,

        trade: Trade

    ):

        self.trades.append(trade)

    def all_trades(self):

        return self.trades

    def winning_trades(self):

        return [

            trade

            for trade in self.trades

            if trade.pnl > 0

        ]

    def losing_trades(self):

        return [

            trade

            for trade in self.trades

            if trade.pnl <= 0

        ]

    def total_pnl(self):

        return sum(

            trade.pnl

            for trade in self.trades

        )

    def trade_count(self):

        return len(

            self.trades

        )