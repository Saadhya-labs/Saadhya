class ExplanationGenerator:


    def generate(
        self,
        report,
        option_result,
        probability
    ):


        reasons = []

        risks = []



        # Stock direction

        if report.direction == "BUY":

            reasons.append(
                "Stock trend confirms bullish direction"
            )

        elif report.direction == "SELL":

            reasons.append(
                "Stock trend confirms bearish direction"
            )



        # Option score

        score = option_result["score"]


        if score >= 90:

            reasons.append(
                "Option quality is excellent"
            )

        elif score >= 75:

            reasons.append(
                "Option quality is good"
            )

        else:

            risks.append(
                "Option quality is weak"
            )



        # Probability

        if probability["confidence"] == "HIGH":

            reasons.append(
                "Trade confidence is high"
            )

        elif probability["confidence"] == "LOW":

            risks.append(
                "Trade confidence is low"
            )



        # Default risks

        if not risks:

            risks.extend(

                [

                    "Market reversal",

                    "Momentum loss"

                ]

            )



        summary = (

            f"{report.direction} opportunity with "

            f"{probability['probability']}% probability"

        )



        return {

            "summary": summary,

            "reasons": reasons,

            "risks": risks

        }