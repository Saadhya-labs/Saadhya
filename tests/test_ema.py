import pandas as pd

from app.indicators.ema import EMAIndicator

prices = [
    100,
    101,
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
]

df = pd.DataFrame({"Close": prices})

ema = EMAIndicator(df)

result = ema.calculate()

print(result.tail())

print("Signal:", ema.signal())