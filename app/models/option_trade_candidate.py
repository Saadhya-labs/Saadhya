from dataclasses import dataclass

from app.options.models import OptionContract


@dataclass
class OptionTradeCandidate:

    symbol: str

    option_contract: OptionContract

    score: int

    recommendation: str

    entry: float

    target: float

    stop_loss: float

    risk_reward: float

    confidence: int