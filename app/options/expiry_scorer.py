from datetime import datetime


class ExpiryScorer:
    """
    Scores option expiry quality.
    """

    def score(self, contract):

        expiry = contract.expiry

        score = 0

        reasons = []


        # Initial architecture supports
        # actual expiry dates later.
        # Current contracts may use labels.

        if expiry in [
            "NEXT_MONTH",
            "FAR_MONTH"
        ]:

            score += 20

            reasons.append(
                "Good time value remaining"
            )


        elif expiry == "CURRENT_MONTH":

            score += 10

            reasons.append(
                "Near expiry with moderate time value"
            )


        else:

            score += 5

            reasons.append(
                "Unknown expiry risk"
            )


        return {

            "score": score,

            "reasons": reasons

        }