class OpportunityRanker:


    def rank(
        self,
        opportunities
    ):


        ranked = sorted(

            opportunities,

            key=lambda x:
                x.get(
                    "score",
                    0
                ),

            reverse=True

        )


        results = []


        previous_score = None

        current_rank = 0


        for position, item in enumerate(
            ranked,
            start=1
        ):


            score = item.get(
                "score",
                0
            )


            if score != previous_score:

                current_rank = position


            result = item.copy()


            result["rank"] = current_rank


            result["rating"] = self._rating(
                score
            )


            results.append(
                result
            )


            previous_score = score


        return results



    def _rating(
        self,
        score
    ):

        if score >= 85:

            return "EXCELLENT OPPORTUNITY"


        if score >= 70:

            return "HIGH PROBABILITY"


        if score >= 50:

            return "WATCH"


        return "AVOID"