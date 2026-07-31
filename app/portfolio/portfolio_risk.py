class PortfolioRisk:


    def __init__(

        self,

        portfolio,

        capital

    ):

        self.portfolio = portfolio
        self.capital = capital



    def invested_amount(self):

        return self.portfolio.invested_amount



    def cash_available(self):

        return self.portfolio.cash



    def exposure_percent(self):

        if self.capital == 0:
            return 0

        return round(

            self.invested_amount()

            /

            self.capital

            *

            100,

            2

        )



    def total_risk(self):

        risk = 0


        for position in self.portfolio.positions:

            risk += abs(

                position.entry_price

                -

                position.stop_loss

            ) * position.quantity


        return round(

            risk,

            2

        )



    def concentration(self):

        result = {}


        for position in self.portfolio.positions:

            value = (

                position.entry_price

                *

                position.quantity

            )


            result[position.symbol] = round(

                value

                /

                self.capital

                *

                100,

                2

            )


        return result



    def report(self):

        warnings = []


        exposure = self.exposure_percent()


        if exposure > 80:

            warnings.append(

                "High portfolio exposure"

            )


        return {

            "capital": self.capital,

            "invested":

                self.invested_amount(),


            "cash":

                self.cash_available(),


            "exposure":

                exposure,


            "risk":

                self.total_risk(),


            "concentration":

                self.concentration(),


            "warnings":

                warnings

        }