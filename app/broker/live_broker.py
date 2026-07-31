from abc import ABC, abstractmethod


class LiveBroker(ABC):


    @abstractmethod
    def connect(self):

        pass


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
    def get_balance(self):

        pass


    @abstractmethod
    def get_positions(self):

        pass