from app.options.intelligence.option_zone_calculator import (
    OptionZoneCalculator
)


class OptionOpportunityEngine:


    def __init__(self):

        self.zone_calculator = (
            OptionZoneCalculator()
        )


    def generate(
        self,
        option
    ):


        zones = self.zone_calculator.calculate(

            option["premium"]

        )


        score = option.get(
            "score",
            0
        )


        if score >= 80:

            rating = "HIGH PROBABILITY"


        elif score >= 60:

            rating = "FAVORABLE"


        else:

            rating = "AVOID"



        return {


            "symbol":

                option["symbol"],


            "contract":

                option["contract"],


            "rating":

                rating,


            "zones":

                zones,


            "scenario":

                "Potential ITM movement"


        }