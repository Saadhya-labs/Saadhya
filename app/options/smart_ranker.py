class SmartOptionRanker:


    def calculate(
        self,
        stock_report,
        option_result
    ):

        option_score = option_result["score"]


        # Stock confidence factor

        stock_factor = (
            stock_report.confidence / 100
        )


        final_score = (
            option_score *
            stock_factor
        )


        # Probability estimate

        probability = min(
            round(final_score * 0.8),
            90
        )


        # Risk classification

        if probability >= 75:
            risk = "LOW"

        elif probability >= 55:
            risk = "MEDIUM"

        else:
            risk = "HIGH"



        return {

            "symbol":
                stock_report.symbol,


            "option":
                option_result["option"],


            "option_score":
                option_score,


            "final_score":
                round(final_score),


            "probability":
                probability,


            "risk":
                risk
        }