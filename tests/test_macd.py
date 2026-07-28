import pandas as pd

from app.indicators.macd import MACDIndicator

prices = [
    100,101,102,103,104,
    105,106,107,108,109,
    110,111,112,113,114,
    115,116,117,118,119,
    120,121,122,123,124,
    125,126,127,128,129,
    130,131,132,133,134,
    135,136,137,138,139
]

df = pd.DataFrame({
    "Close": prices
})

macd = MACDIndicator()

df = macd.calculate(df)

print(df.tail())

latest = df.iloc[-1]

print()
print("MACD:", round(latest["MACD"], 2))
print("Signal Line:", round(latest["MACD_SIGNAL"], 2))
print("Histogram:", round(latest["MACD_HIST"], 2))
print("Trading Signal:", macd.signal(latest))