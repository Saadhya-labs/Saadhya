from abc import ABC, abstractmethod


class Broker(ABC):

    @abstractmethod
    def place_order(
        self,
        symbol,
        direction,
        quantity,
        price
    ):
        pass


    @abstractmethod
    def cancel_order(
        self,
        order_id
    ):
        pass


    @abstractmethod
    def get_orders(self):
        pass