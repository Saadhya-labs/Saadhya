from app.data.market_data import MarketData

market = MarketData()

df = market.get_history("RELIANCE.NS")

print(df.tail())