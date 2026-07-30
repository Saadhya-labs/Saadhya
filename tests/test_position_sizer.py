from app.portfolio.position_sizer import PositionSizer


def test_position_sizer_calculates_quantity():

    sizer = PositionSizer(
        lot_size=25
    )

    quantity = sizer.calculate(
        capital=1_000_000,
        risk_amount=20_000,
        entry_price=100
    )

    assert quantity == 200