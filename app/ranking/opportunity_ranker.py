from app.opportunity.opportunity_report import OpportunityReport


class OpportunityRanker:


    def rank(
        self,
        opportunities
    ):

        ranked = []


        for opportunity in opportunities:

            score = self._calculate_score(
                opportunity
            )

            ranked.append(

                {
                    "symbol": opportunity.symbol,

                    "type": opportunity.instrument_type,

                    "direction": opportunity.direction,

                    "opportunity": opportunity.opportunity,

                    "confidence": opportunity.confidence,

                    "score": score,

                    "expiry": opportunity.expiry,

                    "strike": opportunity.strike,

                }

            )


        ranked.sort(

            key=lambda x: x["score"],

            reverse=True

        )


        for index, item in enumerate(
            ranked,
            start=1
        ):

            item["rank"] = index


        return ranked



    def _calculate_score(
        self,
        opportunity
    ):

        score = 0


        # confidence weight

        score += min(
            opportunity.confidence,
            50
        )


        # opportunity quality

        if opportunity.opportunity == "HIGH PROBABILITY":

            score += 30


        elif opportunity.opportunity == "WATCH":

            score += 15



        # instrument preference

        if opportunity.instrument_type == "OPTION":

            score += 10


        elif opportunity.instrument_type == "STOCK":

            score += 5



        # risk reward

        if opportunity.risk_reward:

            score += min(
                opportunity.risk_reward * 5,
                10
            )


        return int(
            min(score,100)
        )