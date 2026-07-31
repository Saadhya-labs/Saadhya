from app.opportunity.opportunity_scanner import OpportunityScanner


def test_opportunity_scanner_stock():

    scanner = OpportunityScanner()


    result = scanner.scan_stock(

        "HAL.NS",

        {
            "direction":"BUY",
            "confidence":80,
            "technical_reasons":[
                "EMA bullish"
            ]
        }

    )


    assert result.symbol == "HAL.NS"

    assert result.opportunity == "HIGH PROBABILITY"

    assert result.instrument_type == "STOCK"



def test_opportunity_scanner_option():

    scanner = OpportunityScanner()


    result = scanner.scan_option(

        "NIFTY",

        "CURRENT_MONTH",

        25000,

        "BUY",

        75

    )


    assert result.instrument_type == "OPTION"

    assert result.expiry == "CURRENT_MONTH"

    assert result.opportunity == "HIGH PROBABILITY"