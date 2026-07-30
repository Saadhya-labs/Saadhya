from app.market.regime_filter import MarketRegimeFilter



engine = MarketRegimeFilter()



result = engine.analyze(

    nifty="BULLISH",

    banknifty="BULLISH",

    vix="LOW"

)



print("="*60)

print("SAADHYA MARKET REGIME")

print("="*60)


for key,value in result.items():

    print(
        key,
        ":",
        value
    )