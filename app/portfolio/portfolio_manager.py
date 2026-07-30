from app.portfolio.portfolio import Portfolio
from app.portfolio.position import Position


class PortfolioManager:

    def __init__(
        self,
        starting_cash=1_000_000,
        capital=None
    ):

        if capital is not None:
            starting_cash = capital

        self.portfolio = Portfolio(
            cash=starting_cash
        )


    def buy(
        self,
        symbol,
        quantity,
        price,
        stop_loss,
        target
    ):

        position = Position(

            symbol=symbol,

            quantity=quantity,

            entry_price=price,

            current_price=price,

            direction="BUY",

            stop_loss=stop_loss,

            target=target

        )


        self.portfolio.positions.append(
            position
        )


        self.portfolio.cash -= (
            quantity * price
        )


        return position



    def open_position(
        self,
        candidate
    ):

        contract = candidate.option_contract


        quantity = 1


        position = Position(

            symbol=contract.symbol,

            quantity=quantity,

            entry_price=candidate.entry,

            current_price=candidate.entry,

            direction=candidate.recommendation,

            stop_loss=candidate.stop_loss,

            target=candidate.target

        )


        self.portfolio.positions.append(
            position
        )


        self.portfolio.cash -= (
            quantity * candidate.entry
        )


        return position



    def update_price(
        self,
        symbol,
        price
    ):

        for position in self.portfolio.positions:

            if position.symbol == symbol:

                position.current_price = price



    def summary(self):

        return {

            "cash": self.portfolio.cash,

            "invested": self.portfolio.invested_amount,

            "pnl": self.portfolio.total_pnl,

            "positions": len(
                self.portfolio.positions
            )

        }