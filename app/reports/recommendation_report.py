from datetime import datetime, timezone


def projected_roi(reference_price, target, direction="BUY"):
    """Return target upside/downside from the recommendation price, not a guarantee."""
    if reference_price in (None, 0) or target is None:
        return None
    reference = float(reference_price)
    target_price = float(target)
    change = target_price - reference
    if str(direction).upper() == "SELL":
        change = reference - target_price
    return round(change / reference * 100, 2)


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

            current_price = details.get("current_price") if isinstance(details, dict) else None
            target = details.get("target") if isinstance(details, dict) else None
            direction = details.get("direction", "BUY") if isinstance(details, dict) else "BUY"
            entry = details.get("entry") if isinstance(details, dict) else None
            lot_size = None
            one_lot_premium = None
            if item.get("type") == "OPTION" and isinstance(details, dict):
                ranked = details.get("option") or {}
                contract = ranked.get("option") if isinstance(ranked, dict) else None
                if contract is not None:
                    lot_size = getattr(contract, "lot_size", None)
                    one_lot_premium = getattr(contract, "one_lot_premium", None)
                    from app.options.intelligence.option_opportunity_engine import OptionOpportunityEngine
                    premium = float(contract.premium)
                    zones = OptionOpportunityEngine().generate({
                        "symbol": item.get("symbol"),
                        "contract": f"{contract.symbol} {contract.strike:g} {contract.option_type}",
                        "premium": premium,
                        "score": float(item.get("score", 0)),
                    })["zones"]
                    current_price = premium
                    entry = (zones["entry"]["low"], zones["entry"]["high"])
                    target = zones["target"]["low"]
                    direction = "BUY"  # Option premium upside for both long CE and long PE.


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

                    ,"current_price": current_price

                    ,"recommendation_price": current_price

                    ,"lot_size": lot_size

                    ,"one_lot_premium": one_lot_premium

                    ,"entry": entry

                    ,"target": target

                    ,"projected_roi_pct": projected_roi(current_price, target, direction)

                    ,"stop_loss": details.get("stop_loss") if isinstance(details, dict) else None

                    ,"reasons": (
                        list(details.get("simple_reasons", []))
                        + list(details.get("technical_reasons", []))
                    ) if isinstance(details, dict) else []

                }

            )


        return report



    def _recommendation(
        self,
        item
    ):

        details = item.get("details", {})
        if item.get("type") == "STOCK" and isinstance(details, dict):
            recommendation = details.get("recommendation")
            if recommendation:
                return recommendation


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
