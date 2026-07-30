from dataclasses import dataclass


@dataclass
class Position:

    symbol: str

    quantity: int

    entry_price: float

    current_price: float

    direction: str

    stop_loss: float

    target: float

    status: str = "OPEN"

    @property
    def pnl(self):

        if self.direction == "BUY":

            return (
                self.current_price
                - self.entry_price
            ) * self.quantity

        return (
            self.entry_price
            - self.current_price
        ) * self.quantity