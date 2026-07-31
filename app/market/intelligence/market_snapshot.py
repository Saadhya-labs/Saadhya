class MarketSnapshot:


    def analyze(
        self,
        index_data
    ):

        trend = "SIDEWAYS"

        if index_data["close"] > index_data["ema50"]:
            trend = "BULLISH"

        elif index_data["close"] < index_data["ema50"]:
            trend = "BEARISH"


        return {

            "index": index_data["symbol"],

            "close": index_data["close"],

            "trend": trend,

            "volume_status":
                index_data.get(
                    "volume_status",
                    "NORMAL"
                )

        }