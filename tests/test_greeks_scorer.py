from app.options.models import OptionContract
from app.options.greeks_scorer import GreeksScorer


def test_greeks_scorer():

    contract = OptionContract(
        symbol="HAL",
        expiry="NEXT_MONTH",
        strike=1950,
        option_type="CE",
        premium=18,
        volume=900000,
        open_interest=1800000,
        implied_volatility=22,
        delta=0.45,
        theta=-2
    )


    result = GreeksScorer().score(contract)


    assert result["score"] == 20

    assert "Balanced delta exposure" in result["reasons"]

    assert "Controlled time decay" in result["reasons"]