class ExpirySelector:


    def select(
        self,
        expiries,
        preference="CURRENT"
    ):


        if not expiries:
            return None


        if preference == "CURRENT":

            return expiries[0]


        if preference == "NEXT":

            if len(expiries) > 1:
                return expiries[1]


        if preference == "QUARTERLY":

            return expiries[-1]


        return expiries[0]