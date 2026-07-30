class TradeDecision:

    def calculate(self, report):

        price = report.price


        # BUY Setup

        if report.direction == "BUY":

            entry_low = price * 0.995
            entry_high = price * 1.005

            stop_loss = price * 0.95

            target = price * 1.10


            return {
                "action": "SWING BUY",

                "entry": (
                    round(entry_low, 2),
                    round(entry_high, 2)
                ),

                "stop_loss": round(stop_loss, 2),

                "target": round(target, 2),

                "holding": "5-20 days",

                "risk_reward": "1:2"
            }


        # SELL Setup

        elif report.direction == "SELL":

            entry_low = price * 0.995
            entry_high = price * 1.005

            stop_loss = price * 1.05

            target = price * 0.90


            return {

                "action": "SWING SELL",

                "entry": (
                    round(entry_low, 2),
                    round(entry_high, 2)
                ),

                "stop_loss": round(stop_loss, 2),

                "target": round(target, 2),

                "holding": "5-20 days",

                "risk_reward": "1:2"
            }


        return {

            "action": "NO TRADE",

            "reason":
            "Indicators are not aligned"
        }