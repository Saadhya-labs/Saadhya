class OpportunityRanker:


    def rank(self, opportunities):


        ranked = sorted(

            opportunities,

            key=lambda x:
                x["score"],

            reverse=True

        )


        results = []


        for index, item in enumerate(
            ranked,
            start=1
        ):

            item["rank"] = index

            results.append(item)


        return results