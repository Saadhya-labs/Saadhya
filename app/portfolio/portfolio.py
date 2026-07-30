from dataclasses import dataclass, field

from app.portfolio.position import Position


@dataclass
class Portfolio:

    cash: float

    positions: list[Position] = field(default_factory=list)

    @property
    def invested_amount(self):

        total = 0

        for position in self.positions:

            total += (
                position.entry_price
                * position.quantity
            )

        return total

    @property
    def total_pnl(self):

        total = 0

        for position in self.positions:

            total += position.pnl

        return total