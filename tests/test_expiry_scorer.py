from app.options.models import OptionContract
from app.options.expiry_scorer import ExpiryScorer


def test_expiry_scorer():

    contract = OptionContract(
        symbol="HAL",
        expiry="NEXT_MONTH",
        strike=1900,
        option_type="CE",
        premium=25,
        volume=500000,
        open_interest=1500000,
        implied_volatility=22,
        delta=0.45,
        theta=-2
    )


    result = ExpiryScorer().score(contract)


    assert result["score"] == 20

    assert (
        "Good time value remaining"
        in result["reasons"]
    )