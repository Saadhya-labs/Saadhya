from app.portfolio.trade import Trade


class TradeJournal:

    def __init__(self):

        self.trades = []


    def record_trade(

        self,

        trade: Trade

    ):

        self.trades.append(
            trade
        )


    def record(

        self,

        trade: Trade

    ):

        self.record_trade(
            trade
        )


    def all_trades(self):

        return self.trades



    def closed_trades(self):

        return [

            trade

            for trade in self.trades

            if trade.status == "CLOSED"

        ]



    def open_trades(self):

        return [

            trade

            for trade in self.trades

            if trade.status == "OPEN"

        ]



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



    def win_rate(self):

        closed = self.closed_trades()

        if not closed:

            return 0


        winners = [

            trade

            for trade in closed

            if trade.pnl > 0

        ]


        return round(

            len(winners)

            / len(closed)

            * 100,

            2

        )



    def average_pnl(self):

        if not self.trades:

            return 0


        return round(

            self.total_pnl()

            / self.trade_count(),

            2

        )