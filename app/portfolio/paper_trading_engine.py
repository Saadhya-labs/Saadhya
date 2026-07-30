from datetime import datetime

from app.portfolio.trade import Trade


class PaperTradingEngine:

    def __init__(self):

        self.trades = []

    def open_trade(

        self,

        symbol,

        direction,

        quantity,

        entry_price,

        stop_loss,

        target

    ):

        trade = Trade(

            symbol=symbol,

            direction=direction,

            quantity=quantity,

            entry_price=entry_price,

            stop_loss=stop_loss,

            target=target,

            entry_time=datetime.now()

        )

        self.trades.append(trade)

        return trade

    def close_trade(

        self,

        trade,

        exit_price

    ):

        trade.exit_price = exit_price

        trade.exit_time = datetime.now()

        trade.status = "CLOSED"

        if trade.direction == "BUY":

            trade.pnl = (

                exit_price

                - trade.entry_price

            ) * trade.quantity

        else:

            trade.pnl = (

                trade.entry_price

                - exit_price

            ) * trade.quantity

        return trade