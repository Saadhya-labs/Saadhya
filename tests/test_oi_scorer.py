from app.options.models import OptionContract
from app.options.oi_scorer import OIScorer


def test_oi_scorer():

    contract = OptionContract(
        symbol="HAL",
        expiry="CURRENT_MONTH",
        strike=1900,
        option_type="CE",
        premium=25,
        volume=500000,
        open_interest=1500000,
        implied_volatility=22,
        delta=0.45,
        theta=-2
    )


    result = OIScorer().score(contract)


    assert result["score"] == 15

    assert "Strong open interest" in result["reasons"]