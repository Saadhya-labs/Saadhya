from app.config.settings import Settings

from app.data.providers.mock_stock_provider import MockStockProvider
from app.data.providers.nse_stock_provider import NSEStockProvider
from app.data.providers.kite_stock_provider import KiteStockProvider


def get_stock_provider(data_mode=None):

    mode = (data_mode or Settings.DATA_MODE).upper()

    if mode == "MOCK":
        return MockStockProvider()

    if mode == "LIVE":
        return NSEStockProvider()

    if mode == "KITE":
        import os

        return KiteStockProvider(
            api_key=os.environ.get("KITE_API_KEY"),
            access_token=os.environ.get("KITE_ACCESS_TOKEN"),
        )

    raise ValueError(
        f"Unsupported DATA_MODE: {mode}"
    )


def get_option_provider(data_mode=None):
    """Build a recommendation-only option market-data provider."""
    mode = (data_mode or Settings.DATA_MODE).upper()
    if mode == "MOCK":
        from app.data.mock_option_provider import MockOptionProvider
        return MockOptionProvider()
    if mode == "LIVE":
        from app.data.providers.nse_option_provider import NSEOptionProvider
        return NSEOptionProvider()
    if mode == "KITE":
        import os
        from app.data.providers.kite_option_provider import KiteOptionProvider
        return KiteOptionProvider(
            api_key=os.environ.get("KITE_API_KEY"),
            access_token=os.environ.get("KITE_ACCESS_TOKEN"),
        )
    raise ValueError(f"Unsupported DATA_MODE: {mode}")
