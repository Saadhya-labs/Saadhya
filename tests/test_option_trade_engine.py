from app.options.option_trade_engine import OptionTradeEngine
from app.options.option_analyzer import OptionAnalyzer
from app.options.models import OptionContract



def test_option_trade_engine():


    contracts = [

        OptionContract(

            symbol="HAL",

            expiry="NEXT_MONTH",

            strike=1950,

            option_type="CE",

            premium=100,

            volume=900000,

            open_interest=1800000,

            implied_volatility=22,

            delta=0.45,

            theta=-2
        )
    ]


    report = OptionAnalyzer().analyze(
        contracts
    )


    trade = OptionTradeEngine().generate(
        report
    )


    assert trade.symbol == "HAL"

    assert trade.entry == 100

    assert trade.target > trade.entry

    assert trade.stop_loss < trade.entry

    assert trade.risk_reward > 1