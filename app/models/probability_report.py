from dataclasses import dataclass


@dataclass
class ProbabilityReport:

    probability: int

    confidence: str

    factors: list

    warnings: list