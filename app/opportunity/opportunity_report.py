from dataclasses import dataclass, field


@dataclass
class OpportunityReport:

    symbol: str

    instrument_type: str

    direction: str

    opportunity: str

    confidence: float

    entry_zone: dict = field(
        default_factory=dict
    )

    exit_zone: dict = field(
        default_factory=dict
    )

    stop_loss: float = None

    risk_reward: float = None

    expiry: str = None

    strike: float = None

    reasons: list = field(
        default_factory=list
    )

    warnings: list = field(
        default_factory=list
    )


    def to_dict(self):

        return {

            "symbol": self.symbol,

            "instrument_type": self.instrument_type,

            "direction": self.direction,

            "opportunity": self.opportunity,

            "confidence": self.confidence,

            "entry_zone": self.entry_zone,

            "exit_zone": self.exit_zone,

            "stop_loss": self.stop_loss,

            "risk_reward": self.risk_reward,

            "expiry": self.expiry,

            "strike": self.strike,

            "reasons": self.reasons,

            "warnings": self.warnings,

        }