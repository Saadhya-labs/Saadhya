from app.data.providers.option_provider import OptionDataProvider



class NSEOptionProvider(OptionDataProvider):


    def __init__(self):

        pass



    def get_option_chain(
        self,
        symbol
    ):


        raise NotImplementedError(

            "NSE live option data integration pending"

        )