from app.options.market_adjustment import MarketAdjustment



def test_market_adjustment_rewards_aligned_option():


    engine = MarketAdjustment()


    score = engine.adjust(

        80,

        "RISK_ON",

        "CE"

    )


    assert score == 90