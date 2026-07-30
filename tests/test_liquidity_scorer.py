from app.options.models import OptionContract
from app.options.liquidity_scorer import LiquidityScorer


def test_liquidity_scorer():

    contract = OptionContract(
        symbol="HAL",
        expiry="CURRENT_MONTH",
        strike=1900,
        option_type="CE",
        premium=25,
        volume=800000,
        open_interest=1500000,
        implied_volatility=22,
        delta=0.45,
        theta=-2
    )

    result = LiquidityScorer().score(contract)

    assert result["score"] == 20
    assert len(result["reasons"]) == 2