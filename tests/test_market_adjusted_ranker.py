from app.options.market_adjusted_ranker import MarketAdjustedRanker


smart_result = {

    "symbol":"HAL.NS",

    "option":"4600 CE",

    "final_score":90
}


market = {

    "regime":"BULLISH",

    "confidence_adjustment":10

}


result = MarketAdjustedRanker().calculate(
    smart_result,
    market
)


print(result)