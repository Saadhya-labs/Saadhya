from app.scanner.opportunity_ranker import OpportunityRanker



def test_opportunity_ranker_ranks_and_rates():

    opportunities = [

        {
            "symbol": "INFY.NS",
            "score": 60
        },

        {
            "symbol": "HAL.NS",
            "score": 90
        }

    ]


    result = OpportunityRanker().rank(
        opportunities
    )


    assert result[0]["symbol"] == "HAL.NS"

    assert result[0]["rank"] == 1

    assert result[0]["rating"] == "EXCELLENT OPPORTUNITY"

    assert result[1]["rank"] == 2