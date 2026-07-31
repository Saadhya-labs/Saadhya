from dataclasses import dataclass


@dataclass
class Opportunity:

    symbol: str

    instrument_type: str

    expiry: str

    direction: str

    recommendation: str

    confidence: float

    entry_price_low: float

    entry_price_high: float

    exit_price_low: float

    exit_price_high: float

    risk_reward: str

    reasons: list

    risks: list