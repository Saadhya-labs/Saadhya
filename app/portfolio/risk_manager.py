class RiskManager:

    def __init__(

        self,

        risk_percent=2

    ):

        self.risk_percent = risk_percent


    def position_size(

        self,

        capital,

        entry_price,

        stop_loss

    ):

        risk_amount = (

            capital

            * self.risk_percent

            / 100

        )

        risk_per_share = abs(

            entry_price

            - stop_loss

        )

        if risk_per_share == 0:

            return 0

        quantity = int(

            risk_amount

            / risk_per_share

        )

        return quantity


    def max_loss(

        self,

        capital

    ):

        return (

            capital

            * self.risk_percent

            / 100

        )