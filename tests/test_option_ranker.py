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