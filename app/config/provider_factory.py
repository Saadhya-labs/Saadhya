from app.config.settings import DATA_MODE

from app.data.providers.mock_stock_provider import MockStockProvider
from app.data.providers.nse_stock_provider import NSEStockProvider


def get_stock_provider():

    mode = DATA_MODE.upper()

    if mode == "MOCK":
        return MockStockProvider()

    if mode == "LIVE":
        return NSEStockProvider()

    raise ValueError(
        f"Unsupported DATA_MODE: {DATA_MODE}"
    )