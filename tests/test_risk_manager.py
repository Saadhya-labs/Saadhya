from app.portfolio.risk_manager import RiskManager


manager = RiskManager(2)


qty = manager.position_size(

    capital=1_000_000,

    entry_price=4500,

    stop_loss=4400

)


print("=" * 60)
print("SAADHYA RISK MANAGER")
print("=" * 60)

print()

print(

    "Maximum Loss:",

    manager.max_loss(

        1_000_000

    )

)

print(

    "Recommended Quantity:",

    qty

)