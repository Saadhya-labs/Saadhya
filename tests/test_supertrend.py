import pandas as pd

from app.indicators.supertrend import SuperTrendIndicator


df = pd.DataFrame({
    "High": [101,102,103,104,105,106,107,108,109,110,111,112],
    "Low":  [99,100,101,102,103,104,105,106,107,108,109,110],
    "Close":[100,101,102,103,104,105,106,107,108,109,110,111]
})

st = SuperTrendIndicator()

df = st.calculate(df)

print(df.tail())

latest = df.iloc[-1]

print()
print("SuperTrend:", latest["SUPERT"])
print("Direction:", latest["SUPERT_DIRECTION"])
print("Signal:", st.signal(latest))