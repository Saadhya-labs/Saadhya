from datetime import datetime, timezone


class RecommendationReport:

    def __init__(self, limit=10):
        if limit < 1:
            raise ValueError("Report limit must be greater than zero")
        self.limit = limit


    def generate(
        self,
        opportunities,
        metadata=None
    ):


        report = {

            "title":
                "SAADHYA OPPORTUNITY REPORT",

            "total_opportunities":
                len(opportunities),

            "top_opportunities":
                [],

            "generated_at": datetime.now(timezone.utc).isoformat(),

            "recommendation_only": True,

            "metadata": metadata or {}

        }



        for item in opportunities[:self.limit]:


            details = item.get(
                "details",
                {}
            )


            report["top_opportunities"].append(

                {

                    "rank":
                        item.get(
                            "rank"
                        ),

                    "type":
                        item.get(
                            "type"
                        ),

                    "symbol":
                        item.get(
                            "symbol"
                        ),

                    "score":
                        item.get(
                            "score"
                        ),

                    "recommendation":
                        self._recommendation(
                            item
                        ),

                    "risk":
                        self._risk(
                            details
                        ),

                    "warnings": details.get("warnings", []) if isinstance(details, dict) else [],

                    "news_impact": details.get("news_impact", {}).get("impact", "UNAVAILABLE") if isinstance(details, dict) else "UNAVAILABLE"

                }

            )


        return report



    def _recommendation(
        self,
        item
    ):


        score = item.get(
            "score",
            0
        )


        if score >= 85:

            return "HIGH PROBABILITY OPPORTUNITY"


        if score >= 65:

            return "FAVORABLE RISK/REWARD"


        if score >= 40:

            return "WATCH"


        return "AVOID"



    def _risk(
        self,
        details
    ):


        if isinstance(
            details,
            dict
        ):

            if "risk" in details:

                return details["risk"]


        return "MEDIUM"
