from datetime import datetime

from app.broker.broker import Broker
from app.broker.broker_order import BrokerOrder


class PaperBroker(Broker):


    def __init__(self):

        self.orders = []

        self.counter = 1



    def place_order(
        self,
        symbol,
        direction,
        quantity,
        price
    ):

        order = BrokerOrder(

            order_id=self.counter,

            symbol=symbol,

            direction=direction,

            quantity=quantity,

            price=price,

            created_at=datetime.now()

        )

        self.counter += 1


        self.orders.append(
            order
        )

        return order



    def fill_order(
        self,
        order_id
    ):

        for order in self.orders:

            if order.order_id == order_id:

                order.status = "FILLED"

                order.filled_at = datetime.now()

                return order


        return None



    def cancel_order(
        self,
        order_id
    ):

        for order in self.orders:

            if order.order_id == order_id:

                order.status = "CANCELLED"

                return order


        return None



    def get_orders(self):

        return self.orders