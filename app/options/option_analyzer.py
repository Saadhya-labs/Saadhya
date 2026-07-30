from app.models.option_analysis_report import OptionAnalysisReport

from app.options.liquidity_scorer import LiquidityScorer
from app.options.iv_scorer import IVScorer
from app.options.oi_scorer import OIScorer
from app.options.expiry_scorer import ExpiryScorer


class OptionAnalyzer:
    """
    Coordinates option scoring pipeline.
    """

    def __init__(self):

        self.liquidity = LiquidityScorer()

        self.iv = IVScorer()

        self.oi = OIScorer()

        self.expiry = ExpiryScorer()


    def analyze(self, contracts):

        if not contracts:

            raise ValueError(
                "No option contracts supplied."
            )


        best_contract = None

        best_score = -1

        best_breakdown = {}

        reasons = []

        warnings = []


        for contract in contracts:


            liquidity = self.liquidity.score(contract)

            iv = self.iv.score(contract)

            oi = self.oi.score(contract)

            expiry = self.expiry.score(contract)


            total = (
                liquidity["score"]
                +
                iv["score"]
                +
                oi["score"]
                +
                expiry["score"]
            )


            if total > best_score:

                best_score = total

                best_contract = contract


                best_breakdown = {

                    "liquidity": liquidity["score"],

                    "iv": iv["score"],

                    "oi": oi["score"],

                    "expiry": expiry["score"]

                }


                reasons = (
                    liquidity["reasons"]
                    +
                    iv["reasons"]
                    +
                    oi["reasons"]
                    +
                    expiry["reasons"]
                )


        return OptionAnalysisReport(

            best_contract=best_contract,

            score=best_score,

            liquidity_score=best_breakdown["liquidity"],

            iv_score=best_breakdown["iv"],

            oi_score=best_breakdown["oi"],

            expiry_score=best_breakdown["expiry"],

            reasons=reasons,

            warnings=warnings

        )