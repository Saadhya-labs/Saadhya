from dataclasses import dataclass

from app.options.models import OptionContract


@dataclass
class OptionTradeCandidate:

    option_contract: OptionContract

    score: int

    recommendation: str

    entry: float

    target: float

    stop_loss: float

    risk_reward: float

    confidence: int


    @property
    def symbol(self):

        return self.option_contract.symbol