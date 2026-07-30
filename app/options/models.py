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