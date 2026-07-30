class GreeksScorer:
    """
    Scores option Greeks quality.
    """

    def score(self, contract):

        score = 0

        reasons = []

        # Delta quality

        if 0.3 <= contract.delta <= 0.6:

            score += 10

            reasons.append(
                "Balanced delta exposure"
            )

        elif contract.delta > 0:

            score += 5

            reasons.append(
                "Positive directional exposure"
            )


        # Theta decay

        if contract.theta >= -3:

            score += 10

            reasons.append(
                "Controlled time decay"
            )

        else:

            score += 5

            reasons.append(
                "Higher time decay risk"
            )


        return {
            "score": score,
            "reasons": reasons
        }