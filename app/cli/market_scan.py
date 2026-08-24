"""Recommendation-only command-line market scan."""

from __future__ import annotations

from io import TextIOBase
from types import SimpleNamespace
from typing import Any


class _CachedStockScanner:
    """Adapt existing stock reports to the scanner's dictionary contract."""

    def __init__(self, scanner):
        self._scanner = scanner
        self._reports = None

    @property
    def reports(self):
        if self._reports is None:
            self._reports = self._scanner.scan()
        return self._reports

    def scan(self):
        return [
            {
                "symbol": report.symbol,
                "score": report.opportunity_score.get("total", 0),
                "direction": report.direction,
                "confidence": report.confidence,
                "risk": report.risk,
            }
            for report in self.reports
        ]


class _CachedAnalyzer:
    """Serve the already-computed reports to the option scanner."""

    def __init__(self, stock_scanner):
        self._stock_scanner = stock_scanner

    def analyze(self, symbol):
        for report in self._stock_scanner.reports:
            if report.symbol == symbol:
                return report
        raise ValueError(f"No stock analysis report found for {symbol}")


def build_market_scanner():
    """Compose existing analysis, option, and ranking services."""
    from app.config.settings import Settings
    from app.data.mock_option_provider import MockOptionProvider
    from app.data.providers.nse_option_provider import NSEOptionProvider
    from app.options.scanner import OptionScanner
    from app.scanner.market_scanner import MarketScanner
    from app.scanner.option_market_scanner import OptionMarketScanner
    from app.scanner.scanner import StockScanner
    from app.strategy.probability_engine import ProbabilityEngine

    stock_scanner = _CachedStockScanner(StockScanner())
    option_provider = (
        MockOptionProvider()
        if Settings.DATA_MODE.upper() == "MOCK"
        else NSEOptionProvider()
    )
    market_regime = SimpleNamespace(
        regime="NEUTRAL", option_preference="WAIT"
    )
    option_scanner = OptionMarketScanner(
        stock_scanner=stock_scanner,
        analyzer=_CachedAnalyzer(stock_scanner),
        option_provider=option_provider,
        option_scanner=OptionScanner(),
        probability_engine=ProbabilityEngine(),
        market_regime=market_regime,
    )
    return MarketScanner(stock_scanner, option_scanner)


def _format_zone(zone):
    return f"{zone['low']:.2f}–{zone['high']:.2f}"


def format_market_scan(report: dict[str, Any], opportunities: list[dict[str, Any]]):
    """Render existing recommendations with optional option entry/target zones."""
    from app.options.intelligence.option_opportunity_engine import OptionOpportunityEngine
    from app.options.opportunity_formatter import OpportunityFormatter

    lines = [
        "=" * 60,
        report["title"],
        "Recommendation-only: no orders are placed.",
        "=" * 60,
        f"Total opportunities: {report['total_opportunities']}",
    ]
    for item in report["top_opportunities"]:
        lines.extend(
            [
                "",
                f"#{item['rank']} {item['type']} — {item['symbol']}",
                f"Score: {item['score']} | {item['recommendation']} | Risk: {item['risk']}",
            ]
        )

    formatter = OpportunityFormatter()
    zone_engine = OptionOpportunityEngine()
    for item in opportunities[:10]:
        if item.get("type") != "OPTION":
            continue
        option_result = item["details"]["option"]
        formatted = formatter.format(
            {
                "symbol": item["symbol"],
                "direction": item["details"]["direction"],
                "option": option_result,
            }
        )
        opportunity = zone_engine.generate(
            {
                "symbol": formatted["symbol"],
                "contract": formatted["contract"],
                "premium": option_result["option"].premium,
                "score": formatted["score"],
            }
        )
        zones = opportunity["zones"]
        lines.extend(
            [
                f"  Contract: {opportunity['contract']} ({formatted['expiry']})",
                f"  Entry zone: {_format_zone(zones['entry'])}",
                f"  Target zone: {_format_zone(zones['target'])}",
                f"  Invalidation: {zones['invalidation']:.2f}",
            ]
        )
    return "\n".join(lines)


def run(scanner=None, report_generator=None, output: TextIOBase | None = None):
    """Run one market scan and print recommendations; never execute trades."""
    import sys

    if scanner is None:
        scanner = build_market_scanner()
    if report_generator is None:
        from app.core.saadhya_app import SaadhyaApp
        report_generator = SaadhyaApp()
    if output is None:
        output = sys.stdout

    opportunities = scanner.scan()
    report = report_generator.generate_report(opportunities)
    print(format_market_scan(report, opportunities), file=output)
    return report


def main():
    run()


if __name__ == "__main__":
    main()
