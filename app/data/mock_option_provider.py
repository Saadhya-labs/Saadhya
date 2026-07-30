from app.options.models import OptionContract


class MockOptionProvider:


    def get_option_chain(
        self,
        symbol
    ):


        return [

            OptionContract(
                symbol=symbol,
                expiry="CURRENT_MONTH",
                strike=4500,
                option_type="CE",
                premium=100,
                volume=700000,
                open_interest=1500000,
                implied_volatility=22,
                delta=0.45,
                theta=-3
            ),


            OptionContract(
                symbol=symbol,
                expiry="NEXT_MONTH",
                strike=4600,
                option_type="CE",
                premium=120,
                volume=900000,
                open_interest=2500000,
                implied_volatility=24,
                delta=0.55,
                theta=-2
            )

        ]