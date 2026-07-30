from app.options.models import OptionContract
from app.options.option_analyzer import OptionAnalyzer


def test_option_analyzer_selects_best_contract():

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


    report = OptionAnalyzer().analyze(contracts)


    assert report.best_contract.strike == 1950

    assert report.liquidity_score == 20

    assert report.iv_score == 20

    assert report.oi_score == 15

    assert report.expiry_score == 20