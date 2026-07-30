class PositionSizer:

    def __init__(self, lot_size=1):
        self.lot_size = lot_size


    def calculate(
        self,
        capital,
        risk_amount,
        entry_price
    ):

        if entry_price <= 0:
            return 0

        quantity = int(
            risk_amount / entry_price
        )

        lots = quantity // self.lot_size

        return lots * self.lot_size