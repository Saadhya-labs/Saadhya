from app.portfolio.portfolio_manager import PortfolioManager
from app.portfolio.portfolio_risk import PortfolioRisk



def test_portfolio_risk_report():

    manager = PortfolioManager(
        capital=1_000_000
    )


    manager.buy(

        symbol="HAL",

        quantity=200,

        price=4500,

        stop_loss=4400,

        target=4800

    )


    risk = PortfolioRisk(

        manager.portfolio,

        1_000_000

    )


    report = risk.report()


    assert report["invested"] == 900000
    assert report["risk"] == 20000
    assert report["exposure"] == 90