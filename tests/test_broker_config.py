from app.config.broker_config import BrokerConfig


def test_broker_config_defaults_to_paper():

    config = BrokerConfig()


    assert config.get_broker_name() == "paper"