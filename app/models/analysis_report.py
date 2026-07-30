from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AnalysisReport:

    symbol: str

    price: float

    signals: Dict

    recommendation: str

    confidence: int

    direction: str

    opportunity_score: int

    risk: str

    holding: str

    simple_reasons: List[str]

    technical_reasons: List[str]

    suggested_action: str

    invalidation: List[str]