from app.options.models import OptionContract
from app.options.scanner import OptionScanner
from app.options.recommendation import OptionRecommendation


class DummyReport:

    symbol = "HAL.NS"
    direction = "BUY"



contracts = [

    OptionContract(
        symbol="HAL",
        expiry="CURRENT_MONTH",
        strike=4500,
        option_type="CE",
        premium=100,
        volume=700000,
        open_interest=1500000,
        implied_volatility=22,
        delta=0.45,
        theta=-3
    ),


    OptionContract(
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
    ),


    OptionContract(
        symbol="HAL",
        expiry="NEXT_MONTH",
        strike=4700,
        option_type="CE",
        premium=80,
        volume=300000,
        open_interest=800000,
        implied_volatility=35,
        delta=0.30,
        theta=-6
    )

]


scanner = OptionScanner()

ranked = scanner.scan(
    contracts,
    "BUY"
)


engine = OptionRecommendation()


result = engine.generate(
    DummyReport(),
    ranked
)


print("=" * 60)
print("SAADHYA OPTION RECOMMENDATION")
print("=" * 60)

print()

for key, value in result.items():

    print(
        f"{key}: {value}"
    )