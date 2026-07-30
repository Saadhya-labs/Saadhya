import pandas as pd



class MockStockProvider:



    def get_history(
        self,
        symbol,
        period="6mo"
    ):


        close_prices = [

            100,
            101,
            102,
            103,
            105,
            107,
            109,
            111,
            110,
            113,
            115,
            117,
            119,
            121,
            123,
            125,
            127,
            129,
            131,
            133,
            135,
            137,
            139,
            141,
            143,
            145,
            147,
            149,
            151,
            154

        ]


        df = pd.DataFrame({

            "Open":
            [
                x - 1 for x in close_prices
            ],


            "High":
            [
                x + 2 for x in close_prices
            ],


            "Low":
            [
                x - 2 for x in close_prices
            ],


            "Close":
            close_prices,


            "Volume":
            [
                1000000
            ] * len(close_prices)

        })


        return df



    def get_price(
        self,
        symbol
    ):

        return 154