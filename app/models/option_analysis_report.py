from dataclasses import dataclass
from typing import List

from app.options.models import OptionContract


@dataclass
class OptionAnalysisReport:
    best_contract: OptionContract

    score: int

    liquidity_score: int

    iv_score: int

    oi_score: int

    expiry_score: int

    reasons: List[str]

    warnings: List[str]