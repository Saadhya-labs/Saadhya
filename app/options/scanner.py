from app.options.option_ranker import OptionRanker


class OptionScanner:


    def __init__(self):

        self.ranker = OptionRanker()



    def scan(self, contracts, direction):

        results = []


        for option in contracts:


            score = self.ranker.calculate_score(
                option,
                direction
            )


            results.append(
                {
                    "option": option,
                    "score": score["score"],
                    "breakdown": score["breakdown"],
                    "warnings": score["warnings"]
                }
            )


        results.sort(
            key=lambda x:x["score"],
            reverse=True
        )


        return results
