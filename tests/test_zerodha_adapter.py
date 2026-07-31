from app.broker.adapters.zerodha import ZerodhaBroker
from app.broker.broker_credentials import BrokerCredentials


def test_zerodha_adapter_connect():

    credentials = BrokerCredentials(

        api_key="demo",

        api_secret="demo"

    )


    broker = ZerodhaBroker(
        credentials
    )


    result = broker.connect()


    assert result is True