from app.strategy.explanation_generator import ExplanationGenerator
from app.reports.option_report_formatter import OptionReportFormatter
import requests



class OptionMarketScanner:


    def __init__(
        self,
        stock_scanner,
        analyzer,
        option_provider,
        option_scanner,
        probability_engine,
        market_regime
    ):


        self.stock_scanner = stock_scanner

        self.analyzer = analyzer

        self.option_provider = option_provider

        self.option_scanner = option_scanner

        self.probability_engine = probability_engine

        self.market_regime = market_regime

        self.explanation_generator = ExplanationGenerator()

        self.report_formatter = OptionReportFormatter()

        self.failures = []



    def scan(self):

        opportunities = []

        self.failures = []


        stocks = self.stock_scanner.scan()



        for stock in stocks:


            symbol = stock["symbol"]


            report = self.analyzer.analyze(
                symbol
            )



            try:
                options = self.option_provider.get_option_chain(
                    symbol.replace(".NS", "")
                )
            except (requests.RequestException, RuntimeError, ValueError) as exc:
                self.failures.append(
                    {
                        "symbol": symbol,
                        "source": "option-chain",
                        "error": str(exc),
                    }
                )
                continue



            ranked = self.option_scanner.scan(

                options,

                report.direction

            )



            if not ranked:

                continue



            best_option = ranked[0]



            probability = self.probability_engine.calculate(

                option_score=best_option["score"],

                market_regime=self.market_regime.regime

            )



            explanation = self.explanation_generator.generate(

                report,

                best_option,

                probability

            )



            opportunity = {


    "symbol": symbol,

    "direction": report.direction,

    "risk": getattr(report, "risk", "MEDIUM"),

    "option": best_option,

    "probability": probability,

    "market_regime":
        self.market_regime.regime,

    "market_preference":
    getattr(
        self.market_regime,
        "option_preference",
        "UNKNOWN"
    ),

    "explanation": explanation,

    "warnings": best_option.get("warnings", []) + probability.get("warnings", [])

}



            opportunity["formatted_report"] = (

                self.report_formatter.format(

                    opportunity

                )

            )



            opportunities.append(
                opportunity
            )



        return opportunities
