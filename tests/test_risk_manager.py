from app.portfolio.risk_manager import RiskManager


def test_risk_manager_position_size():

    manager = RiskManager(2)

    qty = manager.position_size(
        capital=1_000_000,
        entry_price=4500,
        stop_loss=4400
    )

    assert qty == 200


def test_risk_manager_max_loss():

    manager = RiskManager(2)

    loss = manager.max_loss(
        1_000_000
    )

    assert loss == 20_000