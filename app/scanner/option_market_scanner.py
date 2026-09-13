"""Recommendation-only option scanner across the next three expiries."""

import requests

from app.reports.option_report_formatter import OptionReportFormatter
from app.strategy.explanation_generator import ExplanationGenerator


class OptionMarketScanner:
    def __init__(
        self,
        stock_scanner,
        analyzer,
        option_provider,
        option_scanner,
        probability_engine,
        market_regime,
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
        self.coverage = []

    @staticmethod
    def _underlying(symbol):
        return symbol.upper().replace(".NS", "").replace("NSE:", "")

    def scan(self):
        opportunities = []
        self.failures = []
        self.coverage = []
        stocks = self.stock_scanner.scan()

        batch_chains = None
        get_option_chains = getattr(self.option_provider, "get_option_chains", None)
        if callable(get_option_chains):
            try:
                batch_chains = get_option_chains(
                    self._underlying(stock["symbol"]) for stock in stocks
                )
            except (requests.RequestException, RuntimeError, ValueError) as exc:
                batch_chains = {}
                for stock in stocks:
                    self.failures.append(
                        {
                            "symbol": stock["symbol"],
                            "source": "option-chain",
                            "error": str(exc),
                        }
                    )

        for stock in stocks:
            symbol = stock["symbol"]
            report = self.analyzer.analyze(symbol)
            underlying = self._underlying(symbol)
            coverage = {
                "symbol": symbol,
                "underlying": underlying,
                "status": "unavailable",
                "expiries": [],
                "contract_count": 0,
                "recommendation_count": 0,
            }
            self.coverage.append(coverage)
            if batch_chains is not None:
                options = batch_chains.get(underlying, ())
                if not options:
                    provider_error = getattr(
                        self.option_provider, "chain_failures", {}
                    ).get(underlying, "Option chain was unavailable in the batch response.")
                    if not any(item["symbol"] == symbol for item in self.failures):
                        self.failures.append(
                            {
                                "symbol": symbol,
                                "source": "option-chain",
                                "error": provider_error,
                            }
                        )
                    continue
            else:
                try:
                    options = self.option_provider.get_option_chain(underlying)
                except (requests.RequestException, RuntimeError, ValueError) as exc:
                    self.failures.append(
                        {
                            "symbol": symbol,
                            "source": "option-chain",
                            "error": str(exc),
                        }
                    )
                    continue

            if not options:
                self.failures.append(
                    {
                        "symbol": symbol,
                        "source": "option-chain",
                        "error": "Option chain was empty.",
                    }
                )
                continue

            provider_warnings = []
            instrument_master_stale = bool(
                getattr(self.option_provider, "instrument_master_stale", False)
            )
            if instrument_master_stale:
                provider_warnings.append(
                    "Option contract selection uses the last-known-good Kite instrument "
                    "master while its daily refresh reconnects; contract quotes were "
                    "refreshed separately."
                )
            if underlying in getattr(self.option_provider, "stale_symbols", ()):
                provider_warnings.append(
                    "Option recommendations use last-known-good quotes while Kite reconnects."
                )

            by_expiry = {}
            for contract in options:
                by_expiry.setdefault(contract.expiry, []).append(contract)

            selected_expiries = sorted(by_expiry)
            is_cached = underlying in getattr(self.option_provider, "stale_symbols", ())
            coverage.update({
                "status": "cached" if is_cached else "fresh",
                "expiries": selected_expiries,
                "contract_count": sum(len(by_expiry[expiry]) for expiry in selected_expiries),
            })
            if instrument_master_stale:
                coverage["instrument_master_status"] = "cached"

            # Rank each expiry independently so the nearest expiry cannot
            # crowd the rest of the three-expiry curve out of the results.
            for expiry_rank, expiry in enumerate(selected_expiries, 1):
                # Keep the strongest CE and PE candidate eligible for the
                # cross-market top-ten. This is especially important for
                # NIFTY and other indices; direction alignment remains part
                # of the existing score instead of being bypassed.
                ranked_by_type = []
                option_types = (
                    ("CE", "PE") if underlying == "NIFTY" else
                    ("CE",) if report.direction == "BUY" else
                    ("PE",) if report.direction == "SELL" else
                    ("CE", "PE")
                )
                for option_type in option_types:
                    contracts = [
                        contract for contract in by_expiry[expiry]
                        if contract.option_type == option_type
                    ]
                    ranked = self.option_scanner.scan(contracts, report.direction)
                    if ranked:
                        ranked_by_type.append(ranked[0])

                for best_option in ranked_by_type:
                    probability = self.probability_engine.calculate(
                        option_score=best_option["score"],
                        market_regime=self.market_regime.regime,
                    )
                    explanation = self.explanation_generator.generate(
                        report, best_option, probability
                    )
                    opportunity = {
                        "symbol": symbol,
                        "score": best_option["score"],
                        "direction": report.direction,
                        "risk": getattr(report, "risk", "MEDIUM"),
                        "option": best_option,
                        "probability": probability,
                        "market_regime": self.market_regime.regime,
                        "market_preference": getattr(
                            self.market_regime, "option_preference", "UNKNOWN"
                        ),
                        "explanation": explanation,
                        "expiry": expiry,
                        "expiry_rank": expiry_rank,
                        "expiry_group": (
                            "QUARTERLY"
                            if underlying == "NIFTY" and int(expiry[5:7]) in {3, 6, 9, 12}
                            else "MONTHLY"
                        ),
                        "data_status": "cached" if is_cached else "fresh",
                        "updated_at": getattr(
                            self.option_provider, "chain_updated_at", {}
                        ).get(underlying),
                        "warnings": (
                            best_option.get("warnings", [])
                            + probability.get("warnings", [])
                            + provider_warnings
                        ),
                    }
                    opportunity["formatted_report"] = self.report_formatter.format(
                        opportunity
                    )
                    opportunities.append(opportunity)
                    coverage["recommendation_count"] += 1

        return opportunities
