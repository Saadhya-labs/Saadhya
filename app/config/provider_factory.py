from app.config.settings import Settings

from app.data.providers.mock_stock_provider import MockStockProvider
from app.data.providers.nse_stock_provider import NSEStockProvider


def get_stock_provider(data_mode=None):

    mode = (data_mode or Settings.DATA_MODE).upper()

    if mode == "MOCK":
        return MockStockProvider()

    if mode == "LIVE":
        return NSEStockProvider()

    raise ValueError(
        f"Unsupported DATA_MODE: {mode}"
    )
