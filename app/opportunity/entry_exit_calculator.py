class EntryExitCalculator:


    def calculate(
        self,
        price,
        risk_factor=0.10
    ):

        entry_low = round(
            price * 0.97,
            2
        )

        entry_high = round(
            price,
            2
        )


        exit_low = round(
            price * 1.10,
            2
        )

        exit_high = round(
            price * 1.20,
            2
        )


        return {

            "entry_low": entry_low,

            "entry_high": entry_high,

            "exit_low": exit_low,

            "exit_high": exit_high,

            "risk_reward": "1:2"

        }