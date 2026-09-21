"""Recommendation-only option scanner across the next three expiries."""

from datetime import date

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

    @staticmethod
    def _expiry_group(underlying, expiry):
        """Classify known dated contracts without rejecting provider labels."""
        try:
            expiry_date = date.fromisoformat(str(expiry))
        except (TypeError, ValueError):
            return "MONTHLY"
        return (
            "QUARTERLY"
            if underlying == "NIFTY" and expiry_date.month in {3, 6, 9, 12}
            else "MONTHLY"
        )

    def scan(self):
        opportunities = []
        self.failures = []
        self.coverage = []
        stocks = self.stock_scanner.scan()
        # An all-equities scan can contain thousands of cash-only symbols.
        # Only listed F&O underlyings need option-chain planning and quotes.
        available_fno = getattr(self.option_provider, "available_fno_underlyings", None)
        if callable(available_fno):
            try:
                eligible = {self._underlying(symbol) for symbol in available_fno()}
                stocks = [stock for stock in stocks if self._underlying(stock["symbol"]) in eligible]
            except (requests.RequestException, RuntimeError, ValueError):
                # Preserve the existing per-symbol diagnostic path on a failed master.
                pass

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
            if is_cached and len(selected_expiries) < 3:
                provider_warnings.append(
                    f"Only {len(selected_expiries)} unexpired expiry "
                    f"{'level is' if len(selected_expiries) == 1 else 'levels are'} "
                    "available from cached quotes; the three-expiry curve "
                    "will be checked again after reconnect."
                )
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
                # Retain several independently ranked strikes on both sides.
                # Direction alignment is already reflected in OptionRanker.
                ranked_by_type = []
                for option_type in ("CE", "PE"):
                    contracts = [
                        contract for contract in by_expiry[expiry]
                        if contract.option_type == option_type
                    ]
                    ranked = self.option_scanner.scan(contracts, report.direction)
                    ranked_by_type.extend(ranked[:3])

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
                        "expiry_group": self._expiry_group(underlying, expiry),
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
