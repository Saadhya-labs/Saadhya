from app.portfolio.portfolio_manager import PortfolioManager
from app.models.option_trade_candidate import OptionTradeCandidate
from app.options.models import OptionContract


def test_portfolio_manager_opens_position():

    contract = OptionContract(
        symbol="HAL",
        expiry="NEXT_MONTH",
        strike=1950,
        option_type="CE",
        premium=100,
        volume=900000,
        open_interest=1800000,
        implied_volatility=22,
        delta=0.45,
        theta=-2
    )


    candidate = OptionTradeCandidate(
        option_contract=contract,
        score=80,
        recommendation="BUY",
        entry=100,
        target=130,
        stop_loss=85,
        risk_reward=2.0,
        confidence=80
    )


    manager = PortfolioManager(
        capital=1_000_000
    )


    position = manager.open_position(candidate)


    assert position.symbol == "HAL"
    assert position.quantity > 0
    assert position.status == "OPEN"