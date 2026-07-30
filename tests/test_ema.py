import pandas as pd

from app.indicators.ema import EMAIndicator


def test_ema_indicator():

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

    ema = EMAIndicator()

    result = ema.calculate(df)

    assert "EMA_Short" in result.columns
    assert "EMA_Long" in result.columns

    signal = ema.signal(result.iloc[-1])

    assert signal in {"BUY", "SELL", "HOLD"}