"""Windows desktop interface for Saadhya's recommendation-only workflow."""

from __future__ import annotations

import json
import queue
import re
import threading
import traceback
from io import StringIO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.cli.market_scan import run
from app.core.saadhya_app import SaadhyaApp
from app.reports.recommendation_report import RecommendationReport
from app.reports.recommendation_report import projected_roi
from app.gui.tracking import (
    LocalTrackingStore, contract_key, display_price, expiry_label, group_top_options,
    portfolio_state, quote_change, refresh_tracking_quotes, utc_now,
)
from app.scanner.opportunity_ranker import OpportunityRanker


INDEX_UNDERLYINGS = {
    "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX",
}


def build_option_recommendation_rows(opportunities):
    """Build stable, display-ready rows for the dedicated options workspace."""
    from app.options.intelligence.option_opportunity_engine import OptionOpportunityEngine

    zone_engine = OptionOpportunityEngine()
    rows = []
    for item in opportunities:
        if item.get("type") != "OPTION":
            continue
        details = item["details"]
        ranked = details["option"]
        contract = ranked["option"]
        score = round(float(item.get("score", 0)), 1)
        zones = zone_engine.generate({
            "symbol": item["symbol"],
            "contract": f"{contract.symbol} {contract.strike:g} {contract.option_type}",
            "premium": contract.premium,
            "score": score,
        })["zones"]
        underlying = item["symbol"].upper().replace(".NS", "").replace("NSE:", "")
        warnings = [str(warning) for warning in details.get("warnings", ()) if warning]
        data_status = str(details.get("data_status") or "").lower()
        # Keep warning detection for reports produced before data_status was
        # introduced, but current scans carry an explicit provider state.
        is_cached = data_status == "cached" or (
            not data_status
            and any("last-known-good" in warning.lower() for warning in warnings)
        )
        rows.append({
            "underlying": underlying,
            "asset_class": "INDEX" if underlying in INDEX_UNDERLYINGS else "STOCK",
            "expiry": str(details.get("expiry", contract.expiry)),
            "expiry_rank": details.get("expiry_rank"),
            "expiry_group": details.get("expiry_group", "MONTHLY"),
            "contract": f"{contract.strike:g} {contract.option_type}",
            "direction": details.get("direction", "NEUTRAL"),
            "score": score,
            "strike": contract.strike,
            "option_type": contract.option_type,
            "instrument_type": "OPTION",
            "current_price": float(contract.premium),
            "recommendation_price": float(contract.premium),
            "premium": f"₹{contract.premium:.2f}",
            "lot_size": contract.lot_size,
            "one_lot_premium": contract.one_lot_premium,
            "entry": f"₹{zones['entry']['low']:.2f}–{zones['entry']['high']:.2f}",
            "target": f"₹{zones['target']['low']:.2f}–{zones['target']['high']:.2f}",
            "target_price": float(zones["target"]["low"]),
            "projected_roi_pct": projected_roi(
                contract.premium, zones["target"]["low"], "BUY"
            ),
            "invalidation": f"₹{zones['invalidation']:.2f}",
            "invalidation_price": float(zones["invalidation"]),
            "warnings": warnings,
            "is_cached": is_cached,
            "data_status": "cached" if is_cached else "fresh",
            "market_regime": details.get("market_regime", "UNKNOWN"),
            "explanation": details.get("explanation"),
            # This is a relative recommendation score, not a calibrated
            # probability or promise of an outcome.
            "assessment": (
                "STRONG SETUP" if score >= 85 else
                "FAVORABLE SETUP" if score >= 65 else
                "WATCH" if score >= 40 else "WEAK / AVOID"
            ),
            "updated_at": details.get("updated_at") or details.get("timestamp"),
        })
    return sorted(rows, key=lambda row: (row["expiry"], -row["score"], row["underlying"]))


def option_quote_updated_at(row, generated_at):
    """Use scan time only for fresh quotes lacking a provider timestamp."""
    return row.get("updated_at") or (None if row.get("is_cached") else generated_at)


def stock_overview_opportunities(opportunities, limit=10):
    """Rank stocks from the same scan independently of option contracts."""
    stocks = [item for item in opportunities if item.get("type") == "STOCK"]
    return OpportunityRanker().rank(stocks)[:limit]


def recommendation_rationale(item):
    """Expose only evidence already produced by the analysis pipeline."""
    details = item.get("details", {})
    if item.get("type") == "OPTION":
        explanation = details.get("explanation") or {}
        reasons = [
            reason for reason in explanation.get("reasons", [])
            if reason not in {"Trade confidence is high", "Option quality is excellent", "Option quality is good"}
        ]
        risks = list(explanation.get("risks", []))
        regime = details.get("market_regime")
        if regime and regime != "UNKNOWN":
            reasons.append(f"Market regime: {regime}")
    else:
        reasons = list(details.get("simple_reasons", []))
        technical = list(details.get("technical_reasons", []))
        reasons.extend(reason for reason in technical if reason not in reasons)
        risks = list(details.get("invalidation", []))
    if not reasons:
        reasons = ["Detailed supporting evidence is unavailable for this recommendation."]
    return reasons, risks


def displayed_rationale_items(opportunities, displayed_option_rows):
    """Mirror the stock overview and the visible option expiry tables exactly."""
    stocks = stock_overview_opportunities(opportunities)
    visible = {
        (row["underlying"], row["expiry"], row["contract"])
        for row in displayed_option_rows
    }
    options = []
    seen = set()
    for item in opportunities:
        if item.get("type") != "OPTION":
            continue
        details = item.get("details") or {}
        contract = (details.get("option") or {}).get("option")
        if contract is None:
            continue
        underlying = str(item.get("symbol", "")).upper().replace(".NS", "").replace("NSE:", "")
        key = (underlying, str(details.get("expiry", contract.expiry)),
               f"{contract.strike:g} {contract.option_type}")
        if key in visible and key not in seen:
            options.append(item)
            seen.add(key)
    return stocks + options


def rationale_scenario(item, option_row=None):
    """A conditional path to the target, not a forecast or profit claim."""
    details = item.get("details") or {}
    if option_row is not None:
        side = option_row["option_type"]
        move = "rises" if side == "CE" else "falls"
        return (
            f"Scenario: if {option_row['underlying']} {move} sufficiently before "
            f"{option_row['expiry']}, this {side} premium could move from "
            f"{option_row['premium']} toward the stated target {option_row['target']}. "
            "Volatility, time decay and liquidity can still prevent that outcome. "
            f"The stated invalidation is {option_row['invalidation']}."
        )
    direction = str(details.get("direction") or "WATCH").upper()
    if direction == "BUY":
        return "Scenario: the indicated upward trend would need to continue toward the stated target; a reversal would weaken the setup."
    if direction == "SELL":
        return "Scenario: the indicated downward trend would need to continue toward the stated target; a rebound would weaken the setup."
    return "Scenario: no directional move is established by the current analysis; wait for stronger evidence."


def option_score_evidence(item):
    """Explain the existing option ranker components without calling them odds."""
    ranked = ((item.get("details") or {}).get("option") or {})
    breakdown = ranked.get("breakdown") or {}
    labels = {
        "direction": "Alignment with the underlying trend",
        "liquidity": "Traded volume and open interest",
        "delta": "Delta range",
        "theta": "Time-decay measure",
        "iv": "Implied-volatility range",
    }
    return [
        f"{labels[key]} contributed {float(breakdown[key]):g} ranking points."
        for key in labels if breakdown.get(key, 0) > 0
    ]


def rationale_news(item, underlying_stock=None):
    """Only display headlines actually attached to this scan's analysis."""
    details = item.get("details") or {}
    stock_details = (underlying_stock or {}).get("details") or {}
    news = details.get("news_impact") or stock_details.get("news_impact") or {}
    headlines = [article for article in news.get("headlines", ()) if article.get("title")]
    if not headlines:
        return "No news catalyst was supplied by this scan. The setup is based on technical/contract analysis, not a verified event."
    lines = ["Headlines supplied by this scan (keyword-based context, not proof of a catalyst):"]
    for article in headlines[:3]:
        published = article.get("published_at") or "publication time unavailable"
        lines.append(f"• {article['title']} ({published})")
    return "\n".join(lines)


def option_coverage_summary(rows, metadata=None):
    """Summarize expiry and instrument coverage without implying execution."""
    metadata = metadata or {}
    analysis = metadata.get("option_analysis", ())
    analyzed = [item for item in analysis if item.get("status") in {"fresh", "cached"}]
    if analysis:
        underlyings = {item["underlying"] for item in analyzed}
        attempted = len(analysis)
        expiry_counts = [len(item.get("expiries", ())) for item in analyzed]
        cached_underlyings = sum(item.get("status") == "cached" for item in analyzed)
    else:
        underlyings = {row["underlying"] for row in rows}
        attempted = len(underlyings)
        expiry_counts = [
            len({row["expiry"] for row in rows if row["underlying"] == underlying})
            for underlying in underlyings
        ]
        cached_underlyings = len({
            row["underlying"] for row in rows if row.get("is_cached")
        })
    if not rows and not analyzed:
        return "No option recommendations or usable option chains in this scan."
    indexes = underlyings & INDEX_UNDERLYINGS
    stocks = underlyings - indexes
    failures = sum(
        failure.get("source") == "option-chain"
        for failure in metadata.get("scan_failures", ())
    )
    parts = [
        f"{len(rows)} {'recommendation' if len(rows) == 1 else 'recommendations'}",
        f"{len(underlyings)}/{attempted} chains analyzed ({len(indexes)} index, {len(stocks)} stock)",
        f"{sum(count >= 3 for count in expiry_counts)}/{len(expiry_counts)} "
        "chains cover 3 expiries",
    ]
    if cached_underlyings:
        parts.append(
            f"{cached_underlyings} cached "
            f"{'chain' if cached_underlyings == 1 else 'chains'}"
        )
    if any(item.get("instrument_master_status") == "cached" for item in analysis):
        parts.append("contract master cached")
    if failures:
        parts.append(f"{failures} unavailable {'chain' if failures == 1 else 'chains'}")
    return "  •  ".join(parts)


class SaadhyaDesktopApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.master = master
        self._queue = queue.Queue()
        self.report = None
        self.opportunities = []
        self.mode = tk.StringVar(value="kite")
        self.symbols = tk.StringVar(value="ALL_FNO")
        self.auto_refresh = tk.BooleanVar(value=False)
        self.refresh_seconds = tk.StringVar(value="60")
        self._refresh_job = None
        self._provider_cache = {}
        self._option_rows_by_id = {}
        self._option_tables = {}
        self._checked_option_keys = set()
        self.checked_option_count = tk.StringVar(value="0 checked")
        self._latest_quotes = {}
        self._rationale_rows_by_id = {}
        self._watchlist_rows_by_id = {}
        self._checked_watchlist_keys = set()
        self.checked_watchlist_count = tk.StringVar(value="0 checked")
        self.tracking_store = LocalTrackingStore(Path.home() / ".saadhya" / "tracking.json")
        self.tracking_data = self.tracking_store.load()
        self.status = tk.StringVar(
            value="Ready to scan with the externally configured read-only Kite session. "
            "Recommendations only; no orders are placed."
        )
        self.connection = tk.StringVar(value="KITE / EXTERNAL SESSION")
        self.option_summary = tk.StringVar(value="Run a scan to load index and stock option recommendations.")
        self._build()
        self.pack(fill="both", expand=True)
        self.after(100, self._poll)

    def _build(self):
        self.master.title("Saadhya | Market Intelligence")
        self.master.resizable(True, True)
        self.master.minsize(800, 550)
        self.master.geometry("1280x800")
        self._configure_theme()

        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.pack(fill="x", pady=(0, 0))
        ttk.Label(header, text="SAADHYA", style="Brand.TLabel").pack(side="left")
        ttk.Label(header, text="MARKET INTELLIGENCE  •  RECOMMENDATION ONLY", style="HeaderText.TLabel").pack(side="left", padx=(16, 0))
        ttk.Label(header, text="NO ORDERS", style="Safety.TLabel").pack(side="right")
        ttk.Label(header, textvariable=self.connection, style="Connection.TLabel").pack(side="right", padx=(0, 10))

        controls = ttk.LabelFrame(self, text="Scan controls", padding=12)
        controls.pack(fill="x")
        ttk.Label(controls, text="Universe (ALL_FNO or symbols):").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            controls,
            textvariable=self.symbols,
            values=("ALL_NSE_EQUITIES", "ALL_FNO"),
            state="normal",
            width=52,
        ).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Label(controls, text="Data:").grid(row=0, column=2, sticky="w")
        mode_box = ttk.Combobox(controls, textvariable=self.mode, values=("mock", "live", "kite"), state="readonly", width=9)
        mode_box.grid(row=0, column=3, padx=8)
        mode_box.bind("<<ComboboxSelected>>", self._data_mode_changed)
        self.scan_button = ttk.Button(controls, text="Scan market", command=self.scan)
        self.scan_button.grid(row=0, column=4, padx=(0, 8))
        ttk.Checkbutton(
            controls, text="Auto refresh", variable=self.auto_refresh,
            command=self._refresh_changed,
        ).grid(row=1, column=1, sticky="w", pady=(8, 0))
        ttk.Label(controls, text="Seconds (min 60):").grid(row=1, column=2, sticky="e", pady=(8, 0))
        ttk.Entry(controls, textvariable=self.refresh_seconds, width=9).grid(row=1, column=3, sticky="w", padx=8, pady=(8, 0))
        controls.columnconfigure(1, weight=1)

        ttk.Label(self, textvariable=self.status, style="Status.TLabel", wraplength=1050).pack(fill="x", pady=(10, 6))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        overview = ttk.Frame(notebook, padding=(0, 4, 0, 0))
        options_tab = ttk.Frame(notebook, padding=(0, 4, 0, 0))
        report_tab = ttk.Frame(notebook, padding=12)
        rationale_tab = ttk.Frame(notebook, padding=(0, 4, 0, 0))
        watchlist_tab = ttk.Frame(notebook, padding=(0, 4, 0, 0))
        portfolio_tab = ttk.Frame(notebook, padding=(0, 4, 0, 0))
        notebook.add(overview, text="  Market overview  ")
        notebook.add(options_tab, text="  Options recommendations  ")
        notebook.add(watchlist_tab, text="  Watchlist  ")
        notebook.add(portfolio_tab, text="  Portfolio / Positions  ")
        notebook.add(rationale_tab, text="  Recommendation rationale  ")
        notebook.add(report_tab, text="  JSON report  ")

        self.overview_summary = tk.StringVar(value="Top stock recommendations will appear after a scan. Options are shown by expiry in Options recommendations.")
        ttk.Label(overview, textvariable=self.overview_summary, style="Muted.TLabel").pack(fill="x", padx=4, pady=(2, 4))

        columns = ("rank", "type", "symbol", "recommendation", "recommended", "entry", "target", "roi", "score", "risk", "news")
        table_frame = ttk.Frame(overview)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12, style="Market.Treeview")
        for name, label, width in (
            ("rank", "Rank", 60), ("type", "Type", 90), ("symbol", "Symbol", 130),
            ("recommendation", "Recommendation", 150), ("recommended", "Price at recommendation", 125),
            ("entry", "Entry zone", 120), ("target", "Target", 90),
            ("roi", "Projected ROI", 95), ("score", "Score", 65),
            ("risk", "Risk", 90), ("news", "News", 100),
        ):
            self.table.heading(name, text=label, command=lambda column=name: self._sort_table(self.table, column))
            self.table.column(name, width=width, anchor="center")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        overview_horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=scroll.set, xscrollcommand=overview_horizontal.set)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        overview_horizontal.grid(row=1, column=0, sticky="ew")
        self.table.bind("<<TreeviewSelect>>", self._show_selected)
        self.table.tag_configure("strong", background="#dcfce7", foreground="#166534")
        self.table.tag_configure("watch", background="#fef3c7", foreground="#92400e")
        self.table.tag_configure("avoid", background="#fee2e2", foreground="#991b1b")
        self._add_sort_controls(self.table, (
            ("Score", "score"), ("Projected ROI", "roi"),
            ("Price at recommendation", "recommended"), ("Symbol", "symbol"),
        ))

        details = ttk.LabelFrame(overview, text="Recommendation details and source warnings", padding=8)
        details.pack(fill="both", expand=False, pady=(10, 0))
        self.details = tk.Text(details, height=9, wrap="word", state="disabled")
        self.details.pack(fill="both", expand=True)

        ttk.Label(report_tab, text="Machine-readable report", style="Section.TLabel").pack(anchor="w")
        ttk.Label(report_tab, text="This report is hidden from the market view and available here when needed.", style="Muted.TLabel").pack(anchor="w", pady=(2, 10))
        json_frame = ttk.Frame(report_tab)
        json_frame.pack(fill="both", expand=True)
        self.json_report = tk.Text(json_frame, wrap="none", state="disabled", font=("Consolas", 10))
        json_scroll = ttk.Scrollbar(json_frame, orient="vertical", command=self.json_report.yview)
        self.json_report.configure(yscrollcommand=json_scroll.set)
        self.json_report.pack(side="left", fill="both", expand=True)
        json_scroll.pack(side="right", fill="y")
        self.export_button = ttk.Button(report_tab, text="Export JSON report", command=self.export_json, state="disabled")
        self.export_button.pack(anchor="e", pady=(10, 0))
        legend = ttk.Frame(overview)
        legend.pack(fill="x", pady=(8, 0))
        ttk.Label(legend, text="Colour guide:", style="Muted.TLabel").pack(side="left")
        ttk.Label(legend, text="  Strong opportunity  ", foreground="#166534", background="#dcfce7", padding=(6, 2)).pack(side="left", padx=(8, 0))
        ttk.Label(legend, text="  Watch  ", foreground="#92400e", background="#fef3c7", padding=(6, 2)).pack(side="left", padx=(6, 0))
        ttk.Label(legend, text="  Avoid / weak  ", foreground="#991b1b", background="#fee2e2", padding=(6, 2)).pack(side="left", padx=(6, 0))

        ttk.Label(
            options_tab,
            text="Top 10 index & stock option setups for each exact expiry",
            style="Section.TLabel",
        ).pack(anchor="w", padx=4, pady=(2, 2))
        ttk.Label(
            options_tab, textvariable=self.option_summary, style="Muted.TLabel",
        ).pack(anchor="w", padx=4, pady=(0, 8))
        option_actions = ttk.Frame(options_tab)
        option_actions.pack(fill="x", padx=4, pady=(0, 8))
        ttk.Button(
            option_actions,
            text="Add checked to watchlist",
            command=self._add_selected_to_watchlist,
        ).pack(side="left")
        ttk.Label(
            option_actions, textvariable=self.checked_option_count,
            style="Muted.TLabel",
        ).pack(side="left", padx=(10, 0))
        self.option_category_notebook = ttk.Notebook(options_tab)
        self.option_category_notebook.pack(fill="both", expand=True)
        market_monthly = ttk.Frame(self.option_category_notebook)
        nifty_monthly = ttk.Frame(self.option_category_notebook)
        nifty_quarterly = ttk.Frame(self.option_category_notebook)
        self.option_category_notebook.add(market_monthly, text="  Market monthly top 10  ")
        self.option_category_notebook.add(nifty_monthly, text="  NIFTY monthly  ")
        self.option_category_notebook.add(nifty_quarterly, text="  NIFTY quarterly  ")
        self.expiry_notebook = ttk.Notebook(market_monthly)
        self.nifty_monthly_notebook = ttk.Notebook(nifty_monthly)
        self.nifty_quarterly_notebook = ttk.Notebook(nifty_quarterly)
        for expiry_tabs in (
            self.expiry_notebook, self.nifty_monthly_notebook,
            self.nifty_quarterly_notebook,
        ):
            expiry_tabs.pack(fill="both", expand=True)

        option_details = ttk.LabelFrame(
            options_tab, text="Selected contract and data-quality notes", padding=8,
        )
        option_details.pack(fill="x", pady=(10, 0))
        self.option_details = tk.Text(option_details, height=6, wrap="word", state="disabled")
        self.option_details.pack(fill="x")
        ttk.Button(option_details, text="Add checked to watchlist", command=self._add_selected_to_watchlist).pack(anchor="e", pady=(6, 0))
        self._set_text(
            self.option_details,
            "Select a recommendation to inspect its zones, market regime, and source warnings.",
        )

        self._build_watchlist_tab(watchlist_tab)
        self._build_portfolio_tab(portfolio_tab)
        self._build_rationale_tab(rationale_tab)
        self._render_tracking()
        self._data_mode_changed()

    @staticmethod
    def _tracking_table(parent, columns, sortable=False):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        table = ttk.Treeview(frame, columns=tuple(name for name, _, _ in columns), show="headings", style="Market.Treeview")
        for name, label, width in columns:
            if sortable and name != "selected":
                table.heading(name, text=label, command=lambda column=name: SaadhyaDesktopApp._sort_table(table, column))
            else:
                table.heading(name, text=label)
            table.column(name, width=width, anchor="center")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
        table.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        table.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        return table

    @staticmethod
    def _sort_table(table, column, descending=None):
        """Sort the displayed rows without altering recommendation selection keys."""
        reverse = (
            getattr(table, "_saadhya_sort", None) == (column, False)
            if descending is None else descending
        )
        index = table["columns"].index(column)

        numeric = column in {"strike", "premium", "lot", "value", "roi", "score", "assessment", "reference", "recommended", "current", "change", "percent"}

        def key(item_id):
            value = str(table.item(item_id, "values")[index]).strip()
            number = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", value)
            if numeric and number:
                return float(number.group().replace(",", ""))
            return value.casefold()

        visible = list(table.get_children(""))
        available = [item for item in visible if str(table.item(item, "values")[index]).strip() not in {"", "—", "Unavailable", "Quote unavailable"}]
        missing = [item for item in visible if item not in available]
        if numeric:
            missing.extend(item for item in available if not re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", str(table.item(item, "values")[index])))
            available = [item for item in available if item not in missing]
        for position, item_id in enumerate(sorted(available, key=key, reverse=reverse) + missing):
            table.move(item_id, "", position)
        table._saadhya_sort = (column, reverse)

    @staticmethod
    def _add_sort_controls(table, choices):
        """Visible sorting controls for users who do not discover clickable headings."""
        toolbar = ttk.Frame(table.master.master)
        toolbar.pack(fill="x", padx=4, pady=(2, 5), before=table.master)
        ttk.Label(toolbar, text="Sort by:").pack(side="left", padx=(0, 5))
        labels = {label: column for label, column in choices}
        field = tk.StringVar(value=choices[0][0])
        direction = tk.StringVar(value="High to low")
        field_box = ttk.Combobox(toolbar, textvariable=field, values=tuple(labels), state="readonly", width=24)
        field_box.pack(side="left")
        direction_box = ttk.Combobox(
            toolbar, textvariable=direction, values=("High to low", "Low to high"),
            state="readonly", width=14,
        )
        direction_box.pack(side="left", padx=(8, 0))

        def apply_sort(_event=None):
            SaadhyaDesktopApp._sort_table(table, labels[field.get()], direction.get() == "High to low")

        field_box.bind("<<ComboboxSelected>>", apply_sort)
        direction_box.bind("<<ComboboxSelected>>", apply_sort)
        ttk.Button(toolbar, text="Sort", command=apply_sort).pack(side="left", padx=(8, 0))

    @staticmethod
    def _clear_notebook_tabs(notebook):
        # Forgetting a tab keeps its entire table widget tree alive across scans.
        for tab_id in notebook.tabs():
            notebook.nametowidget(tab_id).destroy()

    def _build_rationale_tab(self, parent):
        ttk.Label(
            parent, text="Why Saadhya flagged each setup", style="Section.TLabel",
        ).pack(anchor="w", padx=4, pady=(2, 2))
        ttk.Label(
            parent,
            text=(
                "Only setups shown in Market overview and Options recommendations appear here. "
                "Projected ROI is a scenario estimate, not a guaranteed return or calibrated probability."
            ),
            style="Muted.TLabel",
        ).pack(anchor="w", padx=4, pady=(0, 8))
        self.rationale_columns = (
            ("type", "Type", 75), ("contract", "Stock / option", 160),
            ("expiry", "Expiry", 100), ("recommended", "Price at recommendation", 130),
            ("target", "Target", 110), ("roi", "Projected ROI", 100),
            ("assessment", "Assessment", 150), ("reason", "Primary reason", 320),
        )
        self.rationale_notebook = ttk.Notebook(parent)
        self.rationale_notebook.pack(fill="both", expand=True)
        stocks_tab = ttk.Frame(self.rationale_notebook)
        options_tab = ttk.Frame(self.rationale_notebook)
        self.rationale_notebook.add(stocks_tab, text="  Stocks  ")
        self.rationale_notebook.add(options_tab, text="  Options by expiry  ")
        self.rationale_stock_table = self._tracking_table(stocks_tab, self.rationale_columns, sortable=True)
        self._add_sort_controls(self.rationale_stock_table, (
            ("Projected ROI", "roi"), ("Price at recommendation", "recommended"),
            ("Assessment", "assessment"), ("Stock", "contract"),
        ))
        self.rationale_stock_table.bind("<<TreeviewSelect>>", self._show_rationale)
        self.rationale_expiry_notebook = ttk.Notebook(options_tab)
        self.rationale_expiry_notebook.pack(fill="both", expand=True)
        details = ttk.LabelFrame(parent, text="Complete rationale and risks", padding=8)
        details.pack(fill="x", pady=(8, 0))
        self.rationale_details = tk.Text(details, height=11, wrap="word", state="disabled")
        rationale_scroll = ttk.Scrollbar(details, orient="vertical", command=self.rationale_details.yview)
        self.rationale_details.configure(yscrollcommand=rationale_scroll.set)
        self.rationale_details.pack(side="left", fill="both", expand=True)
        rationale_scroll.pack(side="right", fill="y")
        self._set_text(self.rationale_details, "Run a scan, then select a recommendation to review its evidence and risks.")

    def _build_watchlist_tab(self, parent):
        ttk.Label(parent, text="Saved recommendations", style="Section.TLabel").pack(anchor="w", padx=4, pady=(2, 2))
        ttk.Label(
            parent,
            text=("Current prices update only from matching scan quotes. Older saved lot sizes "
                  "are filled after a Kite scan confirms the exact contract; otherwise they remain unavailable."),
            style="Muted.TLabel",
        ).pack(anchor="w", padx=4, pady=(0, 8))
        actions = ttk.Frame(parent)
        actions.pack(fill="x", padx=4, pady=(0, 8))
        ttk.Button(actions, text="Remove checked", command=self._remove_selected_watchlist).pack(side="left")
        ttk.Label(
            actions, textvariable=self.checked_watchlist_count, style="Muted.TLabel",
        ).pack(side="left", padx=(10, 0))
        self.watchlist_columns = (
            ("selected", "Remove", 62), ("underlying", "Underlying", 115),
            ("contract", "Contract", 120), ("expiry", "Expiry", 105),
            ("type", "CE/PE", 65), ("strike", "Strike", 80),
            ("reference", "Price at recommendation", 140),
            ("lot", "Lot size", 75), ("value", "One-lot value", 120),
            ("entry", "Entry zone", 125), ("target", "Target / exit", 125),
            ("roi", "Projected ROI", 100), ("risk", "Risk / invalidation", 130),
            ("score", "Score / assessment", 150), ("current", "Current", 95),
            ("change", "Change", 90), ("percent", "Change %", 95),
            ("status", "Status", 165), ("updated", "Last updated", 180),
        )
        self.watchlist_category_notebook = ttk.Notebook(parent)
        self.watchlist_category_notebook.pack(fill="both", expand=True)
        all_saved = ttk.Frame(self.watchlist_category_notebook)
        self.watchlist_category_notebook.add(all_saved, text="  All saved  ")
        self.watchlist_table = self._tracking_table(all_saved, self.watchlist_columns, sortable=True)
        self.watchlist_table.bind("<Button-1>", self._toggle_watchlist_check, add="+")
        self.watchlist_expiry_notebooks = {}
        for category, label in (
            ("market", "Market monthly"), ("nifty_monthly", "NIFTY monthly"),
            ("nifty_quarterly", "NIFTY quarterly"),
        ):
            frame = ttk.Frame(self.watchlist_category_notebook)
            self.watchlist_category_notebook.add(frame, text=f"  {label}  ")
            notebook = ttk.Notebook(frame)
            notebook.pack(fill="both", expand=True)
            self.watchlist_expiry_notebooks[category] = notebook

    def _remove_selected_watchlist(self):
        keys = set(self._checked_watchlist_keys)
        if not keys:
            messagebox.showinfo("Saadhya", "Check one or more watchlist entries to remove.")
            return
        self.tracking_data = self.tracking_store.remove("watchlist", keys)
        self._checked_watchlist_keys.difference_update(keys)
        self.checked_watchlist_count.set("0 checked")
        self._render_tracking()
        self.status.set(f"Removed {len(keys)} item(s) from the local watchlist. No order was placed.")

    def _toggle_watchlist_check(self, event):
        table = event.widget
        if table.identify_region(event.x, event.y) != "cell" or table.identify_column(event.x) != "#1":
            return
        item_id = table.identify_row(event.y)
        key = self._watchlist_rows_by_id.get((table, item_id), self._watchlist_rows_by_id.get(item_id))
        if key is None:
            return "break"
        if key in self._checked_watchlist_keys:
            self._checked_watchlist_keys.remove(key)
            mark = "☐"
        else:
            self._checked_watchlist_keys.add(key)
            mark = "☑"
        for location, visible_key in self._watchlist_rows_by_id.items():
            if visible_key == key:
                visible_table, visible_id = location if isinstance(location, tuple) else (table, location)
                values = list(visible_table.item(visible_id, "values"))
                values[0] = mark
                visible_table.item(visible_id, values=values)
        self.checked_watchlist_count.set(f"{len(self._checked_watchlist_keys)} checked")
        return "break"

    def _build_portfolio_tab(self, parent):
        form = ttk.LabelFrame(parent, text="Add a holding or position to track (no order is placed)", padding=10)
        form.pack(fill="x", pady=(0, 8))
        self.position_kind = tk.StringVar(value="POSITION")
        self.position_contract = tk.StringVar()
        self.position_reference = tk.StringVar()
        self.position_expiry = tk.StringVar()
        for column, (label, variable, width) in enumerate((
            ("Type", self.position_kind, 12), ("Symbol / contract", self.position_contract, 26),
            ("Entered price", self.position_reference, 14), ("Expiry (options)", self.position_expiry, 14),
        )):
            ttk.Label(form, text=label).grid(row=0, column=column * 2, sticky="w", padx=(0, 4))
            if label == "Type":
                widget = ttk.Combobox(form, textvariable=variable, values=("HOLDING", "POSITION"), state="readonly", width=width)
            else:
                widget = ttk.Entry(form, textvariable=variable, width=width)
            widget.grid(row=0, column=column * 2 + 1, padx=(0, 10))
        ttk.Button(form, text="Add to tracker", command=self._add_position).grid(row=0, column=8)
        self.portfolio_table = self._tracking_table(parent, (
            ("kind", "Type", 85), ("contract", "Symbol / contract", 180),
            ("reference", "Entered", 90), ("current", "Current", 100),
            ("change", "P&L / change", 105), ("percent", "Change %", 85),
            ("state", "Saadhya view", 190), ("updated", "Last updated", 160),
        ))

    def _add_position(self):
        contract = self.position_contract.get().strip().upper()
        try:
            reference = float(self.position_reference.get())
        except ValueError:
            messagebox.showerror("Saadhya", "Enter a valid positive entered price.")
            return
        if not contract or reference <= 0:
            messagebox.showerror("Saadhya", "Enter a contract/symbol and a positive price.")
            return
        expiry = self.position_expiry.get().strip()
        item = {
            "instrument_type": "OPTION" if expiry else "STOCK", "underlying": contract,
            "contract": contract, "expiry": expiry, "strike": "", "option_type": "",
            "kind": self.position_kind.get(), "reference_price": reference,
            "current_price": None, "updated_at": None,
        }
        self.tracking_data = self.tracking_store.upsert("positions", item)
        self._render_tracking()
        self.status.set("Tracking item added locally. No order was placed.")

    def _add_selected_to_watchlist(self):
        selected_rows = [
            row for row in self._option_rows_by_id.values()
            if self._option_check_key(row) in self._checked_option_keys
        ]
        if not selected_rows:
            for table in self._option_tables.values():
                selection = table.selection()
                if selection:
                    selected_rows = [self._option_rows_by_id[(table, selection[0])]]
                    break
        if not selected_rows:
            messagebox.showinfo("Saadhya", "Check or select at least one option recommendation first.")
            return
        for selected in selected_rows:
            item = {**selected, "reference_price": selected["current_price"], "added_at": utc_now()}
            self.tracking_data = self.tracking_store.upsert("watchlist", item)
            self._checked_option_keys.discard(self._option_check_key(selected))
        for (table, item_id), row in self._option_rows_by_id.items():
            if row in selected_rows:
                values = list(table.item(item_id, "values"))
                values[0] = "☐"
                table.item(item_id, values=values)
        self.checked_option_count.set("0 checked")
        self._render_tracking()
        self.status.set(f"{len(selected_rows)} recommendation(s) added to the local watchlist. No order was placed.")

    def _refresh_tracking_quotes(self):
        providers = self._provider_cache.get(self.mode.get())
        option_provider = providers[1] if providers else None
        saved_contracts = [
            (item.get("underlying"), item.get("expiry"), item.get("strike"), item.get("option_type"))
            for collection in ("watchlist", "positions")
            for item in self.tracking_data[collection]
            if item.get("instrument_type") == "OPTION" and not item.get("lot_size")
        ]
        lot_sizes = (
            option_provider.lot_sizes_for_contracts(saved_contracts)
            if saved_contracts and callable(getattr(option_provider, "lot_sizes_for_contracts", None))
            else {}
        )
        refresh_tracking_quotes(
            self.tracking_data,
            self._latest_quotes,
            self.report.get("generated_at"),
            lot_sizes=lot_sizes,
        )
        self.tracking_store.save(self.tracking_data)

    @staticmethod
    def _tracking_status(item):
        assessment = item.get("analysis_recommendation") or item.get("assessment", "WATCH")
        freshness = item.get("quote_status")
        return f"{assessment} · {freshness}" if freshness else assessment

    def _render_tracking(self):
        for table in (self.watchlist_table, self.portfolio_table):
            table.delete(*table.get_children())
        for notebook in self.watchlist_expiry_notebooks.values():
            self._clear_notebook_tabs(notebook)
        self._watchlist_rows_by_id = {}
        grouped = {}
        for item in self.tracking_data["watchlist"]:
            self._insert_watchlist_row(self.watchlist_table, item)
            if item.get("instrument_type") != "OPTION" or not item.get("expiry"):
                continue
            category = (
                "nifty_quarterly" if item.get("underlying") == "NIFTY" and item.get("expiry_group") == "QUARTERLY"
                else "nifty_monthly" if item.get("underlying") == "NIFTY"
                else "market"
            )
            grouped.setdefault((category, item["expiry"]), []).append(item)
        for (category, expiry), items in sorted(grouped.items()):
            notebook = self.watchlist_expiry_notebooks[category]
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"  {expiry_label(expiry)}  ")
            table = self._tracking_table(tab, self.watchlist_columns, sortable=True)
            table.bind("<Button-1>", self._toggle_watchlist_check, add="+")
            for item in items:
                self._insert_watchlist_row(table, item)
        for item in self.tracking_data["positions"]:
            change, percent = quote_change(item.get("reference_price"), item.get("current_price"))
            self.portfolio_table.insert("", "end", values=(
                item.get("kind", "POSITION"), item.get("contract"), display_price(item.get("reference_price")),
                display_price(item.get("current_price")), "—" if change is None else f"₹{change:+.2f}",
                "—" if percent is None else f"{percent:+.2f}%", portfolio_state(item),
                item.get("updated_at") or "Quote unavailable",
            ))

    def _insert_watchlist_row(self, table, item):
        change, percent = quote_change(item.get("reference_price"), item.get("current_price"))
        key = contract_key(item)
        def shown(value):
            return value if value not in (None, "") else "Unavailable"
        lot_value = item.get("one_lot_premium")
        roi = item.get("projected_roi_pct")
        score = item.get("score")
        item_id = table.insert("", "end", values=(
            "☑" if key in self._checked_watchlist_keys else "☐",
            shown(item.get("underlying")), shown(item.get("contract")), shown(item.get("expiry")),
            shown(item.get("option_type")), shown(item.get("strike")),
            display_price(item.get("reference_price")), shown(item.get("lot_size")),
            f"₹{lot_value:,.2f}" if lot_value is not None else "Unavailable",
            shown(item.get("entry")), shown(item.get("target")),
            f"{roi:+.2f}%" if roi is not None else "Unavailable",
            shown(item.get("invalidation")),
            f"{score:.1f} · {item.get('assessment', 'WATCH')}" if score is not None else shown(item.get("assessment")),
            display_price(item.get("current_price")),
            "—" if change is None else f"₹{change:+.2f}",
            "—" if percent is None else f"{percent:+.2f}%",
            self._tracking_status(item), item.get("updated_at") or "Quote unavailable",
        ))
        self._watchlist_rows_by_id[(table, item_id)] = key

    def _configure_theme(self):
        style = ttk.Style(self.master)
        style.theme_use("clam")
        background = "#f5f7fb"
        navy = "#16233d"
        accent = "#1f77d0"
        self.master.configure(background=background)
        style.configure("TFrame", background=background)
        style.configure("TLabelframe", background=background)
        style.configure("TLabelframe.Label", background=background, foreground="#334155", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=background, foreground="#172033", font=("Segoe UI", 10))
        style.configure("Header.TFrame", background=navy)
        style.configure("Brand.TLabel", background=navy, foreground="white", font=("Segoe UI", 17, "bold"))
        style.configure("HeaderText.TLabel", background=navy, foreground="#b8c6dc", font=("Segoe UI", 9, "bold"))
        style.configure("Safety.TLabel", background="#203c63", foreground="#d8e9ff", padding=(10, 4), font=("Segoe UI", 9, "bold"))
        style.configure("Connection.TLabel", background="#0f766e", foreground="white", padding=(10, 4), font=("Segoe UI", 9, "bold"))
        style.configure("Status.TLabel", background="#e8f1ff", foreground="#174a84", padding=(10, 8))
        style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Muted.TLabel", foreground="#64748b")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(10, 6))
        style.configure("Market.Treeview", background="white", fieldbackground="white", foreground="#172033", rowheight=32, font=("Segoe UI", 10))
        style.configure("Market.Treeview.Heading", background="#e8eef8", foreground="#334155", font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Market.Treeview", background=[("selected", accent)], foreground=[("selected", "white")])

    def _data_mode_changed(self, _event=None):
        self.scan_button.configure(state="normal")
        if self.mode.get() == "kite":
            self.connection.set("KITE / EXTERNAL SESSION")
            self.status.set(
                "Ready to scan with the externally configured read-only Kite session. "
                "Recommendations only; no orders are placed."
            )
        else:
            self.connection.set("OFFLINE / DEMO" if self.mode.get() == "mock" else "LIVE DATA")

    def scan(self):
        symbols = tuple(item.strip().upper() for item in self.symbols.get().split(",") if item.strip())
        if not symbols:
            messagebox.showerror("Saadhya", "Enter at least one symbol, for example HAL.NS.")
            return
        self._cancel_refresh()
        self.scan_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.status.set(
            "Scanning market data. The first ALL_FNO scan analyses every underlying; "
            "recent history is reused for faster refreshes."
        )
        self.connection.set("CONNECTING" if self.mode.get() != "mock" else "OFFLINE / DEMO")
        threading.Thread(target=self._scan_worker, args=(symbols, self.mode.get()), daemon=True).start()

    def _scan_worker(self, symbols, data_mode):
        try:
            from app.cli.market_scan import build_market_scanner
            from app.config.provider_factory import get_option_provider, get_stock_provider

            providers = self._provider_cache.get(data_mode)
            if providers is None:
                providers = (
                    get_stock_provider(data_mode),
                    get_option_provider(data_mode),
                )
                self._provider_cache[data_mode] = providers
            stock_provider, option_provider = providers

            if data_mode == "kite" and symbols == ("ALL_NSE_EQUITIES",):
                symbols = tuple(dict.fromkeys((
                    *stock_provider.available_nse_equities(), "NIFTY",
                )))
                if not symbols:
                    raise ValueError("Kite returned an empty NSE equity universe.")
            elif data_mode == "kite" and symbols == ("ALL_FNO",):
                symbols = option_provider.available_fno_underlyings()
                if not symbols:
                    raise ValueError("Kite returned an empty F&O universe.")

            scanner = build_market_scanner(
                data_mode=data_mode,
                symbols=symbols,
                stock_provider=stock_provider,
                option_provider=option_provider,
            )
            app = SaadhyaApp(report_engine=RecommendationReport(limit=10))
            output = StringIO()
            report = run(scanner, app, output, data_mode=data_mode)
            self._queue.put(
                ("success", report, scanner.last_opportunities, output.getvalue())
            )
        except Exception:
            self._queue.put(("error", traceback.format_exc()))

    def _poll(self):
        try:
            message = self._queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll)
            return

        if message[0] == "error":
            self._mark_latest_scan_unavailable()
            retry = (
                f" Auto-refresh will retry in {self._refresh_interval()} seconds."
                if self.auto_refresh.get() else ""
            )
            self.status.set(
                "Scan failed; the last successful recommendations remain visible."
                f"{retry}"
            )
            self.connection.set("RECONNECT NEEDED")
            self._set_details(message[1])
        else:
            _, self.report, self.opportunities, rendered = message
            self._render_report(rendered)
            metadata = self.report.get("metadata", {})
            degraded = bool(metadata.get("scan_failures") or metadata.get("stale_data"))
            if degraded:
                self.status.set(
                    f"Scan complete with delayed or unavailable data: "
                    f"{self.report['total_opportunities']} opportunities. No orders were placed."
                )
                self.connection.set("DEGRADED / CACHED")
            else:
                self.status.set(
                    f"Scan complete: {self.report['total_opportunities']} opportunities. "
                    "No orders were placed."
                )
                self.connection.set("LIVE" if self.mode.get() != "mock" else "OFFLINE / DEMO")
            self.export_button.configure(state="normal")
        self.scan_button.configure(state="normal")
        # Re-arm only after the worker is complete and the scan control is usable.
        # This also makes a transient live-data failure retry automatically.
        self._schedule_refresh()
        self.after(100, self._poll)

    def _render_report(self, rendered):
        self.table.delete(*self.table.get_children())
        stocks = stock_overview_opportunities(self.opportunities)
        stock_report = RecommendationReport(limit=10).generate(stocks)
        stock_count = sum(item.get("type") == "STOCK" for item in self.opportunities)
        self.overview_summary.set(
            f"Top {len(stocks)} of {stock_count} stock setups from this scan. "
            "Option contracts are listed by expiry in Options recommendations."
            if stocks else
            "No stock recommendations were available in this scan. Check source warnings; option contracts are listed by expiry in Options recommendations."
        )
        for item in stock_report["top_opportunities"]:
            recommendation = item["recommendation"]
            tag = "strong" if recommendation in {"HIGH PROBABILITY OPPORTUNITY", "FAVORABLE RISK/REWARD"} else "watch" if recommendation == "WATCH" else "avoid"
            entry = item.get("entry")
            entry_text = (
                f"₹{float(entry[0]):.2f}–₹{float(entry[1]):.2f}"
                if isinstance(entry, (list, tuple)) and len(entry) == 2 else "—"
            )
            current = item.get("current_price")
            target = item.get("target")
            roi = item.get("projected_roi_pct")
            self.table.insert("", "end", values=(
                item["rank"], item["type"], item["symbol"], recommendation,
                "—" if current is None else f"₹{float(current):.2f}", entry_text,
                "—" if target is None else f"₹{float(target):.2f}",
                "—" if roi is None else f"{float(roi):+.2f}%",
                item["score"], item["risk"], item.get("news_impact", "UNAVAILABLE"),
            ), tags=(tag,))
        self._set_details(
            "Market overview contains stocks only. Select a stock row for its details. "
            "The JSON report retains the complete scan, including options.\n\n" + rendered
        )
        self._set_json_report(json.dumps(self.report, indent=2))
        self._render_options()
        self._render_rationale()

    def _render_options(self):
        for expiry_tabs in (
            self.expiry_notebook, self.nifty_monthly_notebook,
            self.nifty_quarterly_notebook,
        ):
            self._clear_notebook_tabs(expiry_tabs)
        self._option_tables = {}
        self._option_rows_by_id = {}
        self._set_text(
            self.option_details,
            "Select a recommendation to inspect its zones, market regime, and source warnings.",
        )
        rows = build_option_recommendation_rows(self.opportunities)
        self.option_summary.set(option_coverage_summary(rows, self.report.get("metadata", {})))
        generated_at = self.report.get("generated_at")
        for row in rows:
            row["updated_at"] = option_quote_updated_at(row, generated_at)
        # Rebuild from every recommendation in this scan, including rows below
        # the visual top-ten. Earlier scan rows must never leak into tracking.
        self._latest_quotes = {
            (row["underlying"], row["expiry"], row["contract"]): row
            for row in rows
        }
        for expiry_bucket, expiry_rows in group_top_options(rows).items():
            tab = ttk.Frame(self.expiry_notebook)
            self.expiry_notebook.add(tab, text=f"  {expiry_label(expiry_bucket)}  ")
            columns = (
                ("selected", "Add", 48), ("contract", "Contract", 135), ("underlying", "Underlying", 95),
                ("expiry", "Exact expiry", 105), ("type", "CE/PE", 60),
                ("strike", "Strike", 75), ("premium", "Price at recommendation", 130),
                ("lot", "Lot size", 75), ("value", "One-lot value", 115),
                ("entry", "Entry zone", 110), ("target", "Target / exit", 110),
                ("roi", "Projected ROI", 95), ("invalidation", "Risk / invalidation", 120),
                ("score", "Score / assessment", 125),
                ("freshness", "Updated / freshness", 160),
            )
            table = self._tracking_table(tab, columns, sortable=True)
            self._option_tables[expiry_bucket] = table
            self._add_sort_controls(table, (
                ("Score", "score"), ("Projected ROI", "roi"),
                ("One-lot value", "value"), ("Lot size", "lot"),
                ("Price at recommendation", "premium"), ("Underlying", "underlying"),
            ))
            table.bind("<<TreeviewSelect>>", self._show_selected_option)
            table.bind("<Button-1>", self._toggle_option_check, add="+")
            table.tag_configure("strong", background="#dcfce7", foreground="#166534")
            table.tag_configure("watch", background="#fef3c7", foreground="#92400e")
            table.tag_configure("cached", background="#fff7ed", foreground="#9a3412")
            table.tag_configure("unavailable", background="#f1f5f9", foreground="#64748b")
            for row in expiry_rows:
                is_cached = row["is_cached"]
                freshness = row["updated_at"] or "Timestamp unavailable"
                if is_cached:
                    freshness = f"STALE / cached · {freshness}"
                tag = "cached" if is_cached else "strong" if row["score"] >= 65 else "watch"
                item_id = table.insert("", "end", values=(
                    "☑" if self._option_check_key(row) in self._checked_option_keys else "☐",
                    row["contract"], row["underlying"], row["expiry"],
                    row["option_type"], f"{row['strike']:g}",
                    row["premium"],
                    row["lot_size"] if row["lot_size"] is not None else "—",
                    f"₹{row['one_lot_premium']:,.2f}" if row["one_lot_premium"] is not None else "—",
                    row["entry"], row["target"],
                    f"{row['projected_roi_pct']:+.2f}%", row["invalidation"],
                    f"{row['score']:.1f} · {row['assessment']}", freshness,
                ), tags=(tag,))
                # Treeview-generated IDs repeat across independent tables.
                # Include the table identity so selections resolve to the
                # contract from the active expiry tab.
                self._option_rows_by_id[(table, item_id)] = row
                self._latest_quotes[(row["underlying"], row["expiry"], row["contract"])] = row
        nifty_rows = [row for row in rows if row["underlying"] == "NIFTY"]
        self._render_nifty_expiry_tabs(
            self.nifty_monthly_notebook, nifty_rows, "monthly"
        )
        self._render_nifty_expiry_tabs(
            self.nifty_quarterly_notebook,
            [row for row in nifty_rows if row.get("expiry_group") == "QUARTERLY"],
            "quarterly",
        )
        self._refresh_tracking_quotes()
        self._render_tracking()
        if not rows:
            self._set_text(
                self.option_details,
                "No option contracts met the recommendation criteria in this scan.",
            )

    def _render_nifty_expiry_tabs(self, notebook, rows, group_name):
        by_expiry = {}
        for row in rows:
            by_expiry.setdefault(row["expiry"], []).append(row)
        if not by_expiry:
            empty = ttk.Frame(notebook, padding=16)
            notebook.add(empty, text=f"  No {group_name} data  ")
            ttk.Label(
                empty,
                text=f"No NIFTY {group_name} contracts were available in this scan.",
                style="Muted.TLabel",
            ).pack(anchor="w")
            return

        columns = (
            ("selected", "Add", 48), ("contract", "Contract", 150),
            ("expiry", "Exact expiry", 110), ("type", "CE/PE", 65),
            ("strike", "Strike", 85), ("premium", "Price at recommendation", 130),
            ("lot", "Lot size", 75), ("value", "One-lot value", 115),
            ("entry", "Entry zone", 120), ("target", "Target / exit", 120),
            ("roi", "Projected ROI", 95), ("invalidation", "Risk / invalidation", 125),
            ("score", "Score / assessment", 135), ("freshness", "Updated / freshness", 165),
        )
        for expiry, candidates in sorted(by_expiry.items()):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"  {expiry_label(expiry)}  ")
            table = self._tracking_table(tab, columns, sortable=True)
            self._option_tables[(group_name, expiry)] = table
            self._add_sort_controls(table, (
                ("Score", "score"), ("Projected ROI", "roi"),
                ("One-lot value", "value"), ("Lot size", "lot"),
                ("Price at recommendation", "premium"), ("Strike", "strike"),
            ))
            table.bind("<<TreeviewSelect>>", self._show_selected_option)
            table.bind("<Button-1>", self._toggle_option_check, add="+")
            table.tag_configure("strong", background="#dcfce7", foreground="#166534")
            table.tag_configure("watch", background="#fef3c7", foreground="#92400e")
            table.tag_configure("cached", background="#fff7ed", foreground="#9a3412")
            for row in sorted(candidates, key=lambda item: -item["score"])[:10]:
                is_cached = row["is_cached"]
                freshness = row["updated_at"] or "Timestamp unavailable"
                if is_cached:
                    freshness = f"STALE / cached · {freshness}"
                tag = "cached" if is_cached else "strong" if row["score"] >= 65 else "watch"
                item_id = table.insert("", "end", values=(
                    "☑" if self._option_check_key(row) in self._checked_option_keys else "☐",
                    row["contract"], row["expiry"], row["option_type"], f"{row['strike']:g}",
                    row["premium"],
                    row["lot_size"] if row["lot_size"] is not None else "—",
                    f"₹{row['one_lot_premium']:,.2f}" if row["one_lot_premium"] is not None else "—",
                    row["entry"], row["target"],
                    f"{row['projected_roi_pct']:+.2f}%", row["invalidation"],
                    f"{row['score']:.1f} · {row['assessment']}", freshness,
                ), tags=(tag,))
                self._option_rows_by_id[(table, item_id)] = row

    def _render_rationale(self):
        self.rationale_stock_table.delete(*self.rationale_stock_table.get_children())
        self._clear_notebook_tabs(self.rationale_expiry_notebook)
        self._rationale_rows_by_id = {}
        option_tables = {}
        self._set_text(
            self.rationale_details,
            "Select a recommendation to review its evidence and risks from this scan.",
        )
        displayed_options = list(self._option_rows_by_id.values())
        option_rows = {
            (row["underlying"], row["expiry"], row["contract"]): row
            for row in displayed_options
        }
        stock_by_underlying = {
            str(item.get("symbol", "")).upper().replace(".NS", "").replace("NSE:", ""): item
            for item in self.opportunities if item.get("type") == "STOCK"
        }
        for item in displayed_rationale_items(self.opportunities, displayed_options):
            details = item.get("details", {})
            reasons, risks = recommendation_rationale(item)
            if item.get("type") == "OPTION":
                ranked = details.get("option", {}).get("option")
                if ranked is None:
                    continue
                underlying = str(item.get("symbol", "")).upper().replace(".NS", "").replace("NSE:", "")
                expiry = str(details.get("expiry", ranked.expiry))
                contract = f"{ranked.strike:g} {ranked.option_type}"
                row = option_rows.get((underlying, expiry, contract))
                if row is None:
                    continue
                recommendation_price = row["recommendation_price"]
                target_text = row["target"]
                roi = row["projected_roi_pct"]
                assessment = f"{row['score']:.1f} · {row['assessment']}"
                label = f"{underlying} {contract}"
                reasons.extend(option_score_evidence(item))
                underlying_item = stock_by_underlying.get(underlying)
                if underlying_item:
                    underlying_reasons, _ = recommendation_rationale(underlying_item)
                    reasons.extend(
                        f"Underlying analysis: {reason}" for reason in underlying_reasons
                        if reason != "Detailed supporting evidence is unavailable for this recommendation."
                    )
            else:
                recommendation_price = details.get("current_price")
                target = details.get("target")
                roi = projected_roi(
                    recommendation_price, target, details.get("direction", "BUY")
                )
                target_text = "—" if target is None else f"₹{float(target):.2f}"
                assessment = str(details.get("recommendation") or item.get("rating") or "WATCH")
                label = str(item.get("symbol", "—"))
                expiry = "—"
            if item.get("type") == "OPTION":
                table = option_tables.get(expiry)
                if table is None:
                    tab = ttk.Frame(self.rationale_expiry_notebook)
                    self.rationale_expiry_notebook.add(tab, text=f"  {expiry_label(expiry)}  ")
                    table = self._tracking_table(tab, self.rationale_columns, sortable=True)
                    self._add_sort_controls(table, (
                        ("Projected ROI", "roi"), ("Price at recommendation", "recommended"),
                        ("Assessment", "assessment"), ("Option", "contract"),
                    ))
                    table.bind("<<TreeviewSelect>>", self._show_rationale)
                    option_tables[expiry] = table
            else:
                table = self.rationale_stock_table
            item_id = table.insert("", "end", values=(
                item.get("type", "—"), label, expiry,
                display_price(recommendation_price), target_text,
                "—" if roi is None else f"{roi:+.2f}%", assessment, reasons[0],
            ))
            self._rationale_rows_by_id[(table, item_id)] = {
                "label": label, "reasons": reasons, "risks": risks,
                "recommendation_price": recommendation_price,
                "target": target_text, "roi": roi,
                "scenario": rationale_scenario(item, row if item.get("type") == "OPTION" else None),
                "news": rationale_news(item, stock_by_underlying.get(underlying) if item.get("type") == "OPTION" else None),
                "warnings": list(details.get("warnings") or []),
            }

    def _show_rationale(self, event):
        selection = event.widget.selection()
        if not selection:
            return
        row = self._rationale_rows_by_id.get((event.widget, selection[0]))
        if row is None:
            return
        reasons = "\n".join(f"• {reason}" for reason in row["reasons"])
        risks = "\n".join(f"• {risk}" for risk in row["risks"]) or "• No specific risk detail was supplied; market and liquidity risk still apply."
        warnings = "\n".join(f"• {warning}" for warning in row.get("warnings", ()))
        roi = "Unavailable" if row["roi"] is None else f"{row['roi']:+.2f}% to the stated target"
        self._set_text(
            self.rationale_details,
            f"{row['label']}\n\nWhy it was flagged:\n{reasons}\n\n"
            f"Price at recommendation: {display_price(row['recommendation_price'])}\n"
            f"Target: {row['target']}\nProjected ROI: {roi}\n\n"
            f"{row['scenario']}\n\nNews / catalyst evidence:\n{row['news']}\n\n"
            f"Risks / invalidation:\n{risks}"
            f"{'\n\nData-quality warnings:\n' + warnings if warnings else ''}\n\n"
            "This is a recommendation scenario, not a guaranteed profit or an order.",
        )

    def _show_selected_option(self, _event):
        table = _event.widget
        selection = table.selection()
        if not selection:
            return
        row = self._option_rows_by_id[(table, selection[0])]
        freshness = {
            "cached": "STALE / cached",
            "unavailable": "UNAVAILABLE IN LATEST SCAN",
        }.get(row.get("data_status"), "FRESH")
        one_lot_value = row.get("one_lot_premium")
        one_lot_text = f"₹{one_lot_value:,.2f}" if one_lot_value is not None else "unavailable"
        content = (
            f"{row['underlying']}  {row['contract']}  ·  {row['expiry']}\n"
            f"{row['asset_class']}  ·  Bias {row['direction']}  ·  Score {row['score']}  "
            f"·  Regime {row['market_regime']}\n"
            f"Premium {row['premium']}  ·  Entry {row['entry']}  ·  "
            f"Target {row['target']}  ·  Invalidation {row['invalidation']}\n"
            f"Lot size: {row.get('lot_size') if row.get('lot_size') is not None else 'unavailable'}"
            f"  ·  One-lot premium at recommendation: "
            f"{one_lot_text}\n"
            f"Quote freshness: {freshness}"
            f"  ·  Updated {row['updated_at'] or 'timestamp unavailable'}"
        )
        if row["warnings"]:
            content += "\n\nData-quality notes:\n- " + "\n- ".join(row["warnings"])
        self._set_text(self.option_details, content)

    @staticmethod
    def _option_check_key(row):
        return (row["underlying"], row["expiry"], row["contract"])

    def _toggle_option_check(self, event):
        table = event.widget
        if table.identify_region(event.x, event.y) != "cell" or table.identify_column(event.x) != "#1":
            return
        item_id = table.identify_row(event.y)
        row = self._option_rows_by_id.get((table, item_id))
        if row is None:
            return "break"
        key = self._option_check_key(row)
        if key in self._checked_option_keys:
            self._checked_option_keys.remove(key)
            mark = "☐"
        else:
            self._checked_option_keys.add(key)
            mark = "☑"
        checked = len(self._checked_option_keys)
        self.checked_option_count.set(f"{checked} checked")
        values = list(table.item(item_id, "values"))
        values[0] = mark
        table.item(item_id, values=values)
        return "break"

    def _mark_latest_scan_unavailable(self):
        """Keep last-good rows visible without presenting them as current."""
        for (table, item_id), row in self._option_rows_by_id.items():
            row["data_status"] = "unavailable"
            values = list(table.item(item_id, "values"))
            values[-1] = (
                "UNAVAILABLE in latest scan · last "
                f"{row.get('updated_at') or 'timestamp unavailable'}"
            )
            table.item(item_id, values=values, tags=("unavailable",))

        self._latest_quotes = {}
        if self.report is not None:
            refresh_tracking_quotes(
                self.tracking_data, {}, self.report.get("generated_at")
            )
            self.tracking_store.save(self.tracking_data)
            self._render_tracking()

    def _show_selected(self, _event):
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0], "values")
        symbol = values[2]
        matches = [item for item in self.opportunities if item["symbol"] == symbol]
        warnings = []
        for item in matches:
            warnings.extend(item.get("details", {}).get("warnings", []))
        content = (
            f"{values[2]}\n{values[3]}\nPrice at recommendation: {values[4]} | "
            f"Entry: {values[5]} | Target: {values[6]} | Projected ROI: {values[7]}\n"
            f"Score: {values[8]} | Risk: {values[9]}\n"
            f"News impact: {values[10]}"
        )
        news = next(
            (
                item.get("details", {}).get("news_impact")
                for item in matches
                if item.get("details", {}).get("news_impact")
            ),
            None,
        )
        if news and news.get("headlines"):
            content += "\n\nRecent headlines:\n- " + "\n- ".join(
                article["title"] for article in news["headlines"]
            )
        if warnings:
            content += "\n\nWarnings:\n- " + "\n- ".join(warnings)
        self._set_details(content)

    def _set_details(self, content):
        self._set_text(self.details, content)

    @staticmethod
    def _set_text(widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _set_json_report(self, content):
        self.json_report.configure(state="normal")
        self.json_report.delete("1.0", "end")
        self.json_report.insert("1.0", content)
        self.json_report.configure(state="disabled")

    def export_json(self):
        if self.report is None:
            return
        destination = filedialog.asksaveasfilename(
            title="Save Saadhya report", defaultextension=".json",
            filetypes=(("JSON report", "*.json"),), initialfile="saadhya-report.json",
        )
        if not destination:
            return
        Path(destination).write_text(json.dumps(self.report, indent=2), encoding="utf-8")
        self.status.set(f"Report saved to {destination}")

    def _refresh_changed(self):
        if self.auto_refresh.get():
            self._schedule_refresh()
        else:
            self._cancel_refresh()

    def _refresh_interval(self):
        try:
            return max(60, int(self.refresh_seconds.get()))
        except ValueError:
            return 60

    def _schedule_refresh(self):
        self._cancel_refresh()
        if self.auto_refresh.get() and self.scan_button.instate(("!disabled",)):
            self._refresh_job = self.after(self._refresh_interval() * 1000, self.scan)

    def _cancel_refresh(self):
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)
            self._refresh_job = None


def main():
    root = tk.Tk()
    SaadhyaDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
