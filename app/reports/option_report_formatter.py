class OptionReportFormatter:


    def format(self, opportunity):


        option_data = opportunity["option"]

        option = option_data["option"]

        probability = opportunity["probability"]

        explanation = opportunity["explanation"]



        report = []


        report.append(
            "=" * 60
        )

        report.append(
            "SAADHYA DAILY OPTION OPPORTUNITY"
        )

        report.append(
            "=" * 60
        )



        report.append("")

        report.append(
            f"STOCK: {opportunity['symbol']}"
        )


        report.append(
            f"DIRECTION: {opportunity['direction']}"
        )



        report.append("")

        report.append(
            f"OPTION: {option.strike} {option.option_type}"
        )


        report.append(
            f"EXPIRY: {option.expiry}"
        )



        report.append("")

        report.append(
            f"OPTION SCORE: {option_data['score']}/100"
        )


        report.append(
            f"PROBABILITY: {probability['probability']}%"
        )


        report.append(
            f"CONFIDENCE: {probability['confidence']}"
        )



        report.append("")

        report.append(
            "WHY THIS TRADE:"
        )


        for reason in explanation["reasons"]:

            report.append(
                f"✓ {reason}"
            )



        report.append("")

        report.append(
            "RISK:"
        )


        for risk in explanation["risks"]:

            report.append(
                f"• {risk}"
            )



        report.append("")

        report.append(
            "=" * 60
        )


        return "\n".join(report)