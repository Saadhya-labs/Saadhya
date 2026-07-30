from app.options.models import OptionContract
from app.options.iv_scorer import IVScorer


def test_iv_scorer():

    contract = OptionContract(
        symbol="HAL",
        expiry="CURRENT_MONTH",
        strike=1900,
        option_type="CE",
        premium=25,
        volume=500000,
        open_interest=1000000,
        implied_volatility=22,
        delta=0.45,
        theta=-2
    )


    result = IVScorer().score(contract)


    assert result["score"] == 20

    assert "Healthy implied volatility" in result["reasons"]