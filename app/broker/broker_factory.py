from app.broker.paper_broker import PaperBroker


class BrokerFactory:


    @staticmethod
    def create(
        broker_name="paper"
    ):

        broker_name = broker_name.lower()


        if broker_name == "paper":

            return PaperBroker()


        raise ValueError(

            f"Unsupported broker: {broker_name}"

        )