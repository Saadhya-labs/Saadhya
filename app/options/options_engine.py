from app.options.option_analyzer import OptionAnalyzer


class OptionsEngine:

    def __init__(self):
        self.analyzer = OptionAnalyzer()


    def analyze(self, contracts):

        return self.analyzer.analyze(
            contracts
        )