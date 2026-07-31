from app.market.intelligence.market_snapshot import MarketSnapshot
from app.market.intelligence.market_regime import MarketRegime



def test_market_snapshot_detects_bullish():

    snapshot = MarketSnapshot().analyze(

        {
            "symbol":"NIFTY",
            "close":25000,
            "ema50":24500,
            "volume_status":"HIGH"
        }

    )


    assert snapshot["trend"] == "BULLISH"



def test_market_regime():

    regime = MarketRegime().detect(

        {
            "trend":"BULLISH"
        }

    )


    assert regime["regime"] == "RISK_ON"

    assert regime["option_preference"] == "CALLS"