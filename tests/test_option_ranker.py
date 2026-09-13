from app.options.models import OptionContract
from app.options.option_ranker import OptionRanker


option = OptionContract(

    symbol="HAL",

    expiry="NEXT_MONTH",

    strike=4600,

    option_type="CE",

    premium=120,

    volume=500000,

    open_interest=2000000,

    implied_volatility=24,

    delta=0.55,

    theta=-2.5
)


engine = OptionRanker()


result = engine.calculate_score(
    option,
    "BUY"
)


print(result)


def test_live_kite_style_contracts_receive_distinct_liquidity_scores():
    low = OptionContract("LOW", "2026-09-29", 100, "CE", 10, 5_000, 20_000, 0, 0, 0)
    high = OptionContract("HIGH", "2026-09-29", 100, "CE", 10, 900_000, 5_000_000, 0, 0, 0)

    low_result = engine.calculate_score(low, "BUY")
    high_result = engine.calculate_score(high, "BUY")

    assert high_result["score"] > low_result["score"]
    assert high_result["breakdown"]["liquidity"] > low_result["breakdown"]["liquidity"]
    assert any("Implied volatility is unavailable" in warning for warning in high_result["warnings"])


def test_missing_greeks_are_excluded_from_normalization_not_fabricated():
    contract = OptionContract("NIFTY", "2026-09-29", 25000, "CE", 100, 1_000_000, 10_000_000, 0, 0, 0)
    result = engine.calculate_score(contract, "BUY")
    assert result["score"] == 100
    assert result["breakdown"]["iv"] == 0
