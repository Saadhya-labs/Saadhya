from app.opportunity.opportunity_model import Opportunity
from app.opportunity.entry_exit_calculator import EntryExitCalculator



class OpportunityEngine:


    def __init__(self):

        self.calculator = EntryExitCalculator()



    def generate(

        self,

        symbol,

        price,

        score,

        direction,

        reasons=None

    ):


        if score >= 80:

            recommendation = (
                "HIGH PROBABILITY OPPORTUNITY"
            )


        elif score >= 60:

            recommendation = (
                "FAVORABLE SETUP"
            )


        elif score >= 40:

            recommendation = (
                "WATCHLIST"
            )


        else:

            recommendation = (
                "AVOID"
            )



        levels = self.calculator.calculate(
            price
        )


        if reasons is None:

            reasons = []



        risks = [

            "Market reversal",

            "Volatility change",

            "Liquidity risk"

        ]



        return Opportunity(

            symbol=symbol,

            instrument_type="STOCK",

            expiry="N/A",

            direction=direction,

            recommendation=recommendation,

            confidence=min(
                score,
                100
            ),

            entry_price_low=
                levels["entry_low"],

            entry_price_high=
                levels["entry_high"],

            exit_price_low=
                levels["exit_low"],

            exit_price_high=
                levels["exit_high"],

            risk_reward=
                levels["risk_reward"],

            reasons=reasons,

            risks=risks

        )