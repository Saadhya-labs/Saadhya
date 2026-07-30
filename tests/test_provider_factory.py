from app.config.provider_factory import get_stock_provider


provider = get_stock_provider()

print("=" * 60)
print("PROVIDER FACTORY TEST")
print("=" * 60)

print()

print(type(provider).__name__)