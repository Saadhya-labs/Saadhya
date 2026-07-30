from app.data.providers.mock_stock_provider import MockStockProvider
from app.data.providers.nse_stock_provider import NSEStockProvider



print("="*60)

print(
    "SAADHYA STOCK PROVIDER TEST"
)

print("="*60)



provider = MockStockProvider()



print()

print(
    provider.get_history(
        "HAL.NS"
    )
)



print()

print(
    "Current Price:",
    provider.get_price(
        "HAL.NS"
    )
)



print()

print(
    "NSE Provider Status:"
)



try:

    NSEStockProvider().get_price(
        "HAL.NS"
    )


except NotImplementedError as e:

    print(e)