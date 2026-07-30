from app.options.models import OptionContract
from app.options.smart_ranker import SmartOptionRanker


class DummyStock:

    symbol = "HAL.NS"

    confidence = 90



option = OptionContract(

    symbol="HAL",

    expiry="NEXT_MONTH",

    strike=4600,

    option_type="CE",

    premium=120,

    volume=900000,

    open_interest=2500000,

    implied_volatility=24,

    delta=0.55,

    theta=-2
)


dummy_option_result = {

    "option": option,

    "score": 100
}



engine = SmartOptionRanker()


result = engine.calculate(
    DummyStock(),
    dummy_option_result
)


print("="*60)
print("SMART OPTION RESULT")
print("="*60)

print()

for key,value in result.items():

    print(
        key,
        ":",
        value
    )