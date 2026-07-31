class FinalReportFormatter:


    def format(
        self,
        report
    ):


        market = report["market"]

        stock = report["stock"]

        option = report["option"]


        output = []


        output.append(
            "=" * 60
        )

        output.append(
            "SAADHYA MARKET INTELLIGENCE REPORT"
        )

        output.append(
            "=" * 60
        )


        output.append("")


        output.append(
            f"Market View: {market['view']}"
        )

        output.append(
            f"Regime: {market['regime']}"
        )


        output.append("")

        output.append(
            "TOP STOCK OPPORTUNITY"
        )


        output.append(
            f"Symbol: {stock['symbol']}"
        )


        output.append(
            f"Direction: {stock['direction']}"
        )


        output.append(
            f"Confidence: {stock['confidence']}"
        )


        output.append("")


        output.append(
            "TOP OPTION OPPORTUNITY"
        )


        output.append(
            f"Contract: {option['contract']}"
        )


        output.append(
            f"Expiry: {option['expiry']}"
        )


        output.append(
            f"Scenario: {option['scenario']}"
        )


        output.append(
            f"Entry Zone: {option['entry']}"
        )


        output.append(
            f"Target Zone: {option['target']}"
        )


        output.append(
            f"Risk: {option['risk']}"
        )


        return "\n".join(output)