class StrikeSelector:


    def select(
        self,
        underlying_price,
        strikes,
        direction
    ):


        if direction == "BUY":


            suitable = [

                strike

                for strike in strikes

                if strike <= underlying_price

            ]


        else:


            suitable = [

                strike

                for strike in strikes

                if strike >= underlying_price

            ]


        if suitable:

            return suitable[-1]


        return strikes[0]