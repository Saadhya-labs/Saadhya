from app.options.options_engine import OptionsEngine
from app.options.models import OptionContract


def test_options_engine():

    contracts = [

        OptionContract(
            symbol="HAL",
            expiry="CURRENT_MONTH",
            strike=1900,
            option_type="CE",
            premium=22,
            volume=120000,
            open_interest=300000,
            implied_volatility=40,
            delta=0.45,
            theta=-2
        ),

        OptionContract(
            symbol="HAL",
            expiry="NEXT_MONTH",
            strike=1950,
            option_type="CE",
            premium=18,
            volume=900000,
            open_interest=1800000,
            implied_volatility=22,
            delta=0.40,
            theta=-2
        )
    ]


    engine = OptionsEngine()

    report = engine.analyze(
        contracts
    )


    assert report.best_contract.strike == 1950