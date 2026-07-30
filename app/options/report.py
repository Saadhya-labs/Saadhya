class OptionReport:


    def generate(self, smart_result):

        option = smart_result["option"]


        return {

            "stock":
                smart_result["symbol"],


            "option":
                f"{option.strike} {option.option_type}",


            "expiry":
                option.expiry,


            "premium":
                option.premium,


            "score":
                smart_result["final_score"],


            "probability":
                smart_result["probability"],


            "risk":
                smart_result["risk"],


            "holding":
                "5-15 days"

        }