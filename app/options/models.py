from dataclasses import dataclass


@dataclass
class OptionContract:

    symbol: str

    expiry: str

    strike: float

    option_type: str   # CE or PE

    premium: float

    volume: int

    open_interest: int

    implied_volatility: float

    delta: float

    theta: float

    # Exchange instrument-master quantity; absent for providers that do not
    # supply contract-specific lot sizes. Never assume an index default.
    lot_size: int | None = None

    @property
    def one_lot_premium(self):
        """Premium outlay in rupees for one lot at this contract's quote."""
        if self.lot_size is None or self.lot_size <= 0 or self.premium is None:
            return None
        return round(float(self.premium) * self.lot_size, 2)
