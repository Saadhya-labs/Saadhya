from app.broker.adapters.zerodha import ZerodhaBroker
from app.broker.broker_credentials import BrokerCredentials


def test_live_broker_places_order():

    broker = ZerodhaBroker(

        BrokerCredentials(
            api_key="demo",
            api_secret="demo"
        )

    )


    broker.connect()


    order = broker.place_order(

        symbol="HAL.NS",

        direction="BUY",

        quantity=10,

        price=4500

    )


    assert order["symbol"] == "HAL.NS"

    assert order["direction"] == "BUY"