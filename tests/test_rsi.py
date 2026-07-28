import pandas as pd

from app.indicators.rsi import RSIIndicator

# Sample price data
prices = [
    100,101,102,103,104,
    105,106,107,108,109,
    110,111,112,113,114,
    115,114,113,112,111,
    110,109,108,107,106,
    105,104,103,102,101
]

df = pd.DataFrame({
    "Close": prices
})

rsi = RSIIndicator()

df = rsi.calculate(df)

print(df.tail())

latest = df["RSI"].iloc[-1]

print()
print("Latest RSI:", round(latest, 2))
print("Signal:", rsi.signal(latest))