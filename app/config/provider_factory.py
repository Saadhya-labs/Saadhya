from app.config.settings import DATA_MODE


from app.config.provider_factory import get_stock_provider


# Future
# from app.data.providers.nse_stock_provider import NSEStockProvider



def get_stock_provider():


    if DATA_MODE == "MOCK":

        return MockStockProvider()



    # Future live mode

    # elif DATA_MODE == "LIVE":
    #
    #     return NSEStockProvider()



    raise ValueError(
        "Invalid DATA_MODE"
    )