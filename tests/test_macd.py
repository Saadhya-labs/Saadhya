import pandas as pd

from app.indicators.macd import MACDIndicator


def test_macd_indicator():

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

    result = macd.calculate(df)

    assert "MACD" in result.columns
    assert "MACD_SIGNAL" in result.columns
    assert "MACD_HIST" in result.columns

    latest = result.iloc[-1]

    assert pd.notna(latest["MACD"])
    assert pd.notna(latest["MACD_SIGNAL"])
    assert pd.notna(latest["MACD_HIST"])