from abc import ABC, abstractmethod



class OptionDataProvider(ABC):


    @abstractmethod
    def get_option_chain(
        self,
        symbol
    ):

        pass