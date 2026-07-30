class LiquidityScorer:
    """
    Scores option liquidity using
    volume and open interest.
    """

    def score(self, contract):

        score = 0

        reasons = []

        if contract.volume >= 500000:
            score += 10
            reasons.append("High trading volume")

        elif contract.volume >= 100000:
            score += 5
            reasons.append("Moderate trading volume")

        if contract.open_interest >= 1000000:
            score += 10
            reasons.append("Strong open interest")

        elif contract.open_interest >= 250000:
            score += 5
            reasons.append("Moderate open interest")

        return {
            "score": score,
            "reasons": reasons
        }