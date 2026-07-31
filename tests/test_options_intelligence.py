from app.options.intelligence.expiry_selector import ExpirySelector
from app.options.intelligence.option_opportunity_engine import OptionOpportunityEngine



def test_expiry_selector():

    result = ExpirySelector().select(

        [
            "2026-08",
            "2026-09",
            "2026-Q3"
        ]

    )

    assert result == "2026-08"



def test_option_opportunity():

    result = OptionOpportunityEngine().generate(

        {

            "symbol":"NIFTY",

            "contract":"24500 CE",

            "premium":100,

            "score":90

        }

    )


    assert result["rating"] == "HIGH PROBABILITY"

    assert result["zones"]["entry"]["low"] == 90