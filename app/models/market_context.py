from dataclasses import dataclass


@dataclass
class MarketContext:

    nifty: str

    sensex: str

    banknifty: str

    vix: str

    market_bias: str