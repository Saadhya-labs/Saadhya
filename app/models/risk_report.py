from dataclasses import dataclass


@dataclass
class RiskReport:

    risk_level: str

    stop_loss: float | None

    target: float | None

    risk_reward: float | None