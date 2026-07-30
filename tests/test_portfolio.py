from app.portfolio.portfolio_manager import PortfolioManager


manager = PortfolioManager()


manager.buy(

    symbol="HAL.NS",

    quantity=10,

    price=4500,

    stop_loss=4350,

    target=4900

)


manager.update_price(

    "HAL.NS",

    4581.40

)


print("=" * 60)
print("SAADHYA PORTFOLIO TEST")
print("=" * 60)

print()

print(manager.summary())