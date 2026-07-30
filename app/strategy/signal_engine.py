from app.indicators.ema import EMAIndicator
from app.indicators.rsi import RSIIndicator
from app.indicators.macd import MACDIndicator
from app.indicators.vwap import VWAPIndicator
from app.indicators.supertrend import SuperTrendIndicator



class SignalEngine:


    def __init__(self):

        self.ema = EMAIndicator()

        self.rsi = RSIIndicator()

        self.macd = MACDIndicator()

        self.vwap = VWAPIndicator()

        self.supertrend = SuperTrendIndicator()



    def generate(
        self,
        data
    ):


        signals = {}


        # EMA

        ema_data = self.ema.calculate(data)

        ema_row = ema_data.iloc[-1]

        signals["EMA"] = self.ema.signal(
            ema_row
        )



        # RSI

        rsi_data = self.rsi.calculate(data)

        rsi_value = rsi_data.iloc[-1]["RSI"]

        signals["RSI"] = self.rsi.signal(
            rsi_value
        )



        # MACD

        macd_data = self.macd.calculate(data)

        macd_row = macd_data.iloc[-1]


        if (
            macd_row["MACD"]
            >
            macd_row["MACD_SIGNAL"]
        ):

            signals["MACD"] = "BUY"


        elif (
            macd_row["MACD"]
            <
            macd_row["MACD_SIGNAL"]
        ):

            signals["MACD"] = "SELL"


        else:

            signals["MACD"] = "HOLD"



        # VWAP

        vwap_data = self.vwap.calculate(data)

        vwap_row = vwap_data.iloc[-1]

        signals["VWAP"] = self.vwap.signal(
            vwap_row
        )



        # SuperTrend

        st_data = self.supertrend.calculate(data)

        st_row = st_data.iloc[-1]

        signals["SUPERTREND"] = self.supertrend.signal(
            st_row
        )


        return signals