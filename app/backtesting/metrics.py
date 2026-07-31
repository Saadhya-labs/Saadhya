class BacktestMetrics:


    def calculate(self, performance):

        return {

            "trades":
                performance["trades"],

            "wins":
                performance["wins"],

            "losses":
                performance["losses"],

            "win_rate":
                performance["win_rate"],

            "profit_factor":
                performance["profit_factor"],

            "net_profit":
                performance["net_profit"],

            "expectancy":
                performance["expectancy"]

        }