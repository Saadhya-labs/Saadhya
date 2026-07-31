from app.broker.broker_factory import BrokerFactory


def test_broker_factory_creates_paper_broker():

    broker = BrokerFactory.create(
        "paper"
    )


    assert broker is not None

    assert broker.__class__.__name__ == "PaperBroker"