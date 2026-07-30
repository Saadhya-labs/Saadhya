class OIScorer:
    """
    Scores option open interest strength.
    """

    def score(self, contract):

        oi = contract.open_interest

        score = 0

        reasons = []

        if oi >= 2000000:

            score += 20

            reasons.append(
                "Very strong open interest"
            )

        elif oi >= 1000000:

            score += 15

            reasons.append(
                "Strong open interest"
            )

        elif oi >= 250000:

            score += 8

            reasons.append(
                "Moderate open interest"
            )

        else:

            score += 3

            reasons.append(
                "Low open interest"
            )


        return {

            "score": score,

            "reasons": reasons

        }