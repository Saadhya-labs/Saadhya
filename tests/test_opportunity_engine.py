from app.opportunity.opportunity_engine import OpportunityEngine



def test_opportunity_engine_generates_opportunity():


    engine = OpportunityEngine()


    result = engine.generate(

        symbol="HAL.NS",

        price=4500,

        score=85,

        direction="BUY"

    )


    assert result.symbol == "HAL.NS"

    assert (
        result.recommendation
        ==
        "HIGH PROBABILITY OPPORTUNITY"
    )

    assert result.entry_price_low > 0

    assert result.exit_price_high > result.exit_price_low

    assert result.risk_reward == "1:2"