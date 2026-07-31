class BrokerConfig:


    def __init__(
        self,
        broker_name="paper"
    ):

        self.broker_name = broker_name


    def get_broker_name(self):

        return self.broker_name