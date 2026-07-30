class IVScorer:
    """
    Scores option implied volatility.
    """

    def score(self, contract):

        iv = contract.implied_volatility

        reasons = []

        score = 0


        if 15 <= iv <= 30:

            score += 20

            reasons.append(
                "Healthy implied volatility"
            )


        elif iv < 15:

            score += 10

            reasons.append(
                "Low volatility environment"
            )


        else:

            score += 5

            reasons.append(
                "High volatility risk"
            )


        return {

            "score": score,

            "reasons": reasons

        }