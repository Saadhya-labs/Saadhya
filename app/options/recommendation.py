class OptionRecommendation:


    def generate(self, stock_report, ranked_options):

        if not ranked_options:

            return {
                "recommendation": "NO OPTION FOUND"
            }


        best = ranked_options[0]


        option = best["option"]


        return {

            "stock":
                stock_report.symbol,

            "direction":
                stock_report.direction,


            "option":
                f"{option.strike} {option.option_type}",


            "expiry":
                option.expiry,


            "premium":
                option.premium,


            "score":
                best["score"],


            "breakdown":
                best["breakdown"],


            "holding":
                "5-15 days"

        }