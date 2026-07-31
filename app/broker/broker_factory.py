from app.broker.paper_broker import PaperBroker
from app.broker.adapters.zerodha import ZerodhaBroker


class BrokerFactory:


    @staticmethod
    def create(
        broker_name="paper",
        credentials=None
    ):

        broker_name = broker_name.lower()


        if broker_name == "paper":

            return PaperBroker()


        if broker_name == "zerodha":

            return ZerodhaBroker(
                credentials
            )


        raise ValueError(

            f"Unsupported broker: {broker_name}"

        )