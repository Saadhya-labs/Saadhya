class OpportunityFormatter:


    def format(self, opportunity):


        option_result = opportunity["option"]

        option = option_result["option"]


        return {


            "symbol":
                opportunity["symbol"],


            "direction":
                opportunity["direction"],


            "contract":
                f"{option.strike} {option.option_type}",


            "expiry":
                option.expiry,


            "premium":
                option.premium,


            "score":
                option_result["score"],


            "breakdown":
                option_result["breakdown"]

        }