import pandas as pd

from app.indicators.vwap import VWAPIndicator


df = pd.DataFrame({
    "High": [101, 102, 103, 104, 105],
    "Low": [99, 100, 101, 102, 103],
    "Close": [100, 101, 102, 103, 104],
    "Volume": [1000, 1200, 1100, 1300, 1400]
})

vwap = VWAPIndicator()

df = vwap.calculate(df)

print(df)

latest = df.iloc[-1]

print()
print("Latest VWAP:", round(latest["VWAP"], 2))
print("Signal:", vwap.signal(latest))