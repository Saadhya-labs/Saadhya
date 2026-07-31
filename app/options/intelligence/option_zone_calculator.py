class OptionZoneCalculator:


    def calculate(
        self,
        premium
    ):


        return {


            "entry":

            {

                "low":
                    round(
                        premium * 0.90,
                        2
                    ),

                "high":
                    round(
                        premium * 1.10,
                        2
                    )

            },


            "target":

            {

                "low":
                    round(
                        premium * 1.50,
                        2
                    ),

                "high":
                    round(
                        premium * 2.00,
                        2
                    )

            },


            "invalidation":

                round(
                    premium * 0.70,
                    2
                )

        }