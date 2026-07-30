class OptionChain:

    def __init__(self, symbol):

        self.symbol = symbol

        self.contracts = []


    def add(self, contract):

        self.contracts.append(contract)


    def get_calls(self):

        return [
            c for c in self.contracts
            if c.option_type == "CE"
        ]


    def get_puts(self):

        return [
            c for c in self.contracts
            if c.option_type == "PE"
        ]