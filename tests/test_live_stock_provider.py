from app.data.providers.nse_stock_provider import NSEStockProvider


provider = NSEStockProvider()


print("=" * 60)
print("LIVE STOCK PROVIDER TEST")
print("=" * 60)


price = provider.get_price(

    "HAL.NS"

)


print()

print(

    "Current Price:",

    price

)


print()


history = provider.get_history(

    "HAL.NS"

)


print(

    history.tail()

)