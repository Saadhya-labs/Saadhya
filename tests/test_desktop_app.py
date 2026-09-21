import queue
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_desktop_application_module_is_importable():
    from app.gui.desktop import SaadhyaDesktopApp
    from app.scanner.universe import NSE_STOCKS

    assert SaadhyaDesktopApp.__name__ == "SaadhyaDesktopApp"
    assert len(NSE_STOCKS) > 1


def test_market_overview_selects_stocks_without_option_rows():
    from app.gui.desktop import stock_overview_opportunities

    opportunities = [
        {"type": "OPTION", "symbol": "NIFTY", "score": 100, "details": {}},
        {"type": "STOCK", "symbol": "HAL", "score": 72, "details": {}},
        {"type": "STOCK", "symbol": "TCS", "score": 82, "details": {}},
    ]
    rows = stock_overview_opportunities(opportunities)
    assert [row["symbol"] for row in rows] == ["TCS", "HAL"]
    assert [row["rank"] for row in rows] == [1, 2]


def test_rationale_matches_visible_stock_and_option_recommendations():
    from app.gui.desktop import displayed_rationale_items
    from app.options.models import OptionContract

    opportunities = [
        {"type": "STOCK", "symbol": f"STOCK{i}", "score": 100 - i, "details": {}}
        for i in range(12)
    ]
    for strike in (100, 110):
        contract = OptionContract("NIFTY", "2026-09-29", strike, "CE", 10, 1, 1, 0, 0, 0)
        opportunities.append({
            "type": "OPTION", "symbol": "NIFTY", "score": 80,
            "details": {"option": {"option": contract}, "expiry": contract.expiry},
        })
    shown = displayed_rationale_items(opportunities, [{
        "underlying": "NIFTY", "expiry": "2026-09-29", "contract": "110 CE",
    }])
    assert len(shown) == 11
    assert sum(item["type"] == "STOCK" for item in shown) == 10
    assert shown[-1]["details"]["option"]["option"].strike == 110


def test_rationale_scenario_and_news_do_not_invent_catalysts():
    from app.gui.desktop import option_score_evidence, rationale_news, rationale_scenario

    item = {"type": "OPTION", "details": {}}
    row = {
        "option_type": "PE", "underlying": "NIFTY", "expiry": "2026-09-29",
        "premium": "₹10.00", "target": "₹15.00–₹20.00", "invalidation": "₹7.00",
    }
    assert "falls" in rationale_scenario(item, row)
    assert "time decay" in rationale_scenario(item, row)
    assert "No news catalyst" in rationale_news(item)
    with_news = {"details": {"news_impact": {"headlines": [{
        "title": "Results announcement", "published_at": "2026-09-17",
    }]}}}
    assert "Results announcement" in rationale_news(with_news)
    score_reasons = option_score_evidence({"details": {"option": {"breakdown": {
        "direction": 25, "liquidity": 12.5, "delta": 0,
    }}}})
    assert any("underlying trend" in reason for reason in score_reasons)
    assert any("12.5" in reason for reason in score_reasons)
    assert all("probability" not in reason.lower() for reason in score_reasons)


class Variable:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class Button:
    def __init__(self, state="disabled"):
        self.state = state

    def configure(self, state):
        self.state = state


class FakeCheckTable:
    def __init__(self):
        self.rows = {"I001": ["☐", "25000 CE"]}

    def identify_region(self, _x, _y):
        return "cell"

    def identify_column(self, _x):
        return "#1"

    def identify_row(self, _y):
        return "I001"

    def item(self, item_id, option=None, **kwargs):
        if option == "values":
            return tuple(self.rows[item_id])
        if "values" in kwargs:
            self.rows[item_id] = list(kwargs["values"])


def test_watchlist_first_column_toggles_a_remove_checkbox():
    from app.gui.desktop import SaadhyaDesktopApp

    table = FakeCheckTable()
    key = "OPTION|NIFTY|2026-09-24|25000|CE"
    app = SimpleNamespace(
        _watchlist_rows_by_id={"I001": key},
        _checked_watchlist_keys=set(),
        checked_watchlist_count=Variable("0 checked"),
    )
    event = SimpleNamespace(widget=table, x=1, y=1)

    assert SaadhyaDesktopApp._toggle_watchlist_check(app, event) == "break"
    assert table.rows["I001"][0] == "☑"
    assert app._checked_watchlist_keys == {key}
    assert app.checked_watchlist_count.get() == "1 checked"

    SaadhyaDesktopApp._toggle_watchlist_check(app, event)
    assert table.rows["I001"][0] == "☐"
    assert app._checked_watchlist_keys == set()


def test_recommendation_table_sorts_numeric_value_and_score():
    from app.gui.desktop import SaadhyaDesktopApp

    class Table:
        _saadhya_sort = None
        def __init__(self):
            self.order = ["low", "high"]
            self.rows = {"low": ("₹900.00", "60.0 · WATCH"), "high": ("₹1,200.00", "85.0 · STRONG")}
        def __getitem__(self, key):
            assert key == "columns"
            return ("value", "score")
        def item(self, item_id, _option):
            return self.rows[item_id]
        def get_children(self, _root):
            return self.order
        def move(self, item_id, _root, position):
            self.order.remove(item_id)
            self.order.insert(position, item_id)

    table = Table()
    SaadhyaDesktopApp._sort_table(table, "value")
    assert table.order == ["low", "high"]
    SaadhyaDesktopApp._sort_table(table, "value")
    assert table.order == ["high", "low"]
    SaadhyaDesktopApp._sort_table(table, "score")
    assert table.order == ["low", "high"]
    SaadhyaDesktopApp._sort_table(table, "score", descending=True)
    assert table.order == ["high", "low"]


def test_watchlist_row_shows_underlying_and_recommendation_details():
    from app.gui.desktop import SaadhyaDesktopApp

    class Table:
        def insert(self, _parent, _where, values):
            self.values = values
            return "I001"

    table = Table()
    app = SimpleNamespace(
        _checked_watchlist_keys=set(), _watchlist_rows_by_id={},
        _tracking_status=SaadhyaDesktopApp._tracking_status,
    )
    item = {
        "instrument_type": "OPTION", "underlying": "NIFTY", "contract": "25000 CE",
        "expiry": "2026-09-29", "strike": 25000, "option_type": "CE",
        "reference_price": 100, "current_price": 110, "lot_size": 75,
        "one_lot_premium": 7500, "entry": "₹90–110", "target": "₹150–200",
        "projected_roi_pct": 50, "invalidation": "₹70", "score": 85,
        "assessment": "STRONG SETUP",
    }
    SaadhyaDesktopApp._insert_watchlist_row(app, table, item)
    assert table.values[1:4] == ("NIFTY", "25000 CE", "2026-09-29")
    assert "₹7,500.00" in table.values
    assert "85.0 · STRONG SETUP" in table.values


def test_kite_mode_uses_externally_configured_session_without_login_gate():
    from app.gui.desktop import SaadhyaDesktopApp

    app = SimpleNamespace(
        mode=Variable("kite"),
        scan_button=Button("disabled"),
        connection=Variable(),
        status=Variable(),
    )

    SaadhyaDesktopApp._data_mode_changed(app)

    assert app.scan_button.state == "normal"
    assert app.connection.get() == "KITE / EXTERNAL SESSION"
    assert "externally configured" in app.status.get()

    source = (PROJECT_ROOT / "app/gui/desktop.py").read_text(encoding="utf-8")
    assert "KiteLogin" not in source
    assert "connect_kite" not in source
    assert "KITE_API_SECRET" not in source
    assert 'self.symbols = tk.StringVar(value="ALL_FNO")' in source
    assert not (PROJECT_ROOT / "app/integrations/kite_login.py").exists()


def test_projected_roi_and_rationale_use_existing_analysis_evidence():
    from app.gui.desktop import recommendation_rationale
    from app.reports.recommendation_report import projected_roi

    item = {
        "type": "STOCK",
        "details": {
            "simple_reasons": ["Buying momentum is increasing."],
            "technical_reasons": ["MACD Bullish"],
            "invalidation": ["Momentum reversal"],
        },
    }
    reasons, risks = recommendation_rationale(item)
    assert reasons == ["Buying momentum is increasing.", "MACD Bullish"]
    assert risks == ["Momentum reversal"]
    assert projected_roi(100, 112, "BUY") == 12.0
    assert projected_roi(100, 90, "SELL") == 10.0
    assert projected_roi(None, 112, "BUY") is None


def test_option_workspace_summarizes_three_expiries_and_cached_quotes():
    from app.gui.desktop import build_option_recommendation_rows, option_coverage_summary
    from app.options.models import OptionContract

    opportunities = []
    for symbol, expiry, warning in (
        ("NIFTY", "2026-09-03", ""),
        ("HAL.NS", "2026-09-10", "Option recommendations use last-known-good quotes while Kite reconnects."),
        ("HAL.NS", "2026-09-17", ""),
    ):
        contract = OptionContract(
            symbol, expiry, 100, "CE", 10, 100000, 200000, 20, .5, -.1
        )
        opportunities.append({
            "type": "OPTION",
            "symbol": symbol,
            "score": 75,
            "details": {
                "option": {"option": contract, "score": 80},
                "expiry": expiry,
                "direction": "BUY",
                "market_regime": "NEUTRAL",
                "warnings": [warning] if warning else [],
            },
        })

    rows = build_option_recommendation_rows(opportunities)
    summary = option_coverage_summary(rows, {
        "scan_failures": [{"symbol": "TCS", "source": "option-chain"}],
    })

    assert [row["expiry"] for row in rows] == [
        "2026-09-03", "2026-09-10", "2026-09-17",
    ]
    assert {row["asset_class"] for row in rows} == {"INDEX", "STOCK"}
    assert summary == (
        "3 recommendations  •  2/2 chains analyzed (1 index, 1 stock)  •  "
        "0/2 chains cover 3 expiries  •  1 cached chain  •  1 unavailable chain"
    )


def test_option_workspace_prefers_explicit_cached_status_over_warning_text():
    from app.gui.desktop import build_option_recommendation_rows
    from app.options.models import OptionContract

    contract = OptionContract(
        "HAL", "2026-09-24", 100, "CE", 10, 100000, 200000, 20, .5, -.1
    )
    rows = build_option_recommendation_rows([{
        "type": "OPTION", "symbol": "HAL.NS", "score": 75,
        "details": {
            "option": {"option": contract, "score": 80},
            "expiry": contract.expiry, "direction": "BUY",
            "data_status": "cached", "warnings": ["Provider reconnecting."],
        },
    }])

    assert rows[0]["is_cached"] is True
    assert rows[0]["data_status"] == "cached"


def test_cached_option_without_quote_time_does_not_inherit_scan_time():
    from app.gui.desktop import option_quote_updated_at

    scan_time = "2026-09-17T06:30:00+00:00"
    assert option_quote_updated_at({"is_cached": True}, scan_time) is None
    assert option_quote_updated_at({"is_cached": False}, scan_time) == scan_time
    assert option_quote_updated_at(
        {"is_cached": True, "updated_at": "2026-09-17T06:00:00+00:00"},
        scan_time,
    ) == "2026-09-17T06:00:00+00:00"


def test_option_workspace_summary_uses_analyzed_chain_coverage():
    from app.gui.desktop import option_coverage_summary

    metadata = {"option_analysis": [
        {
            "underlying": "NIFTY", "status": "fresh",
            "expiries": ["2026-09-03", "2026-09-10", "2026-09-17"],
        },
        {
            "underlying": "HAL", "status": "cached",
            "expiries": ["2026-10-29", "2026-11-26"],
        },
        {"underlying": "TCS", "status": "unavailable", "expiries": []},
    ], "scan_failures": [{"symbol": "TCS", "source": "option-chain"}]}

    summary = option_coverage_summary([{"underlying": "NIFTY"}], metadata)

    assert summary == (
        "1 recommendation  •  2/3 chains analyzed (1 index, 1 stock)  •  "
        "1/2 chains cover 3 expiries  •  1 cached chain  •  1 unavailable chain"
    )


def test_option_workspace_summary_discloses_cached_contract_master():
    from app.gui.desktop import option_coverage_summary

    metadata = {"option_analysis": [{
        "underlying": "NIFTY", "status": "fresh",
        "expiries": ["2026-09-24"], "instrument_master_status": "cached",
    }]}

    summary = option_coverage_summary([{"underlying": "NIFTY"}], metadata)

    assert summary.endswith("contract master cached")


def test_failed_scan_rearms_auto_refresh_after_enabling_scan_control():
    from app.gui.desktop import SaadhyaDesktopApp

    messages = queue.Queue()
    messages.put(("error", "temporary disconnect"))
    button = Button()
    scheduled_states = []
    app = SimpleNamespace(
        _queue=messages,
        status=Variable(),
        connection=Variable(),
        auto_refresh=Variable(True),
        mode=Variable("mock"),
        scan_button=button,
        _refresh_interval=lambda: 60,
        _set_details=lambda content: None,
        _mark_latest_scan_unavailable=lambda: None,
        _schedule_refresh=lambda: scheduled_states.append(button.state),
        after=lambda delay, callback: None,
        _poll=lambda: None,
    )

    SaadhyaDesktopApp._poll(app)

    assert button.state == "normal"
    assert scheduled_states == ["normal"]
    assert app.connection.get() == "RECONNECT NEEDED"
    assert "retry in 60 seconds" in app.status.get()


def test_expiry_refresh_destroys_old_tab_widgets():
    from app.gui.desktop import SaadhyaDesktopApp

    class Tab:
        def __init__(self, notebook, name):
            self.notebook = notebook
            self.name = name
            self.destroyed = False

        def destroy(self):
            self.destroyed = True
            self.notebook.children.pop(self.name)

    class Notebook:
        def __init__(self):
            self.children = {}

        def tabs(self):
            return tuple(self.children)

        def nametowidget(self, tab_id):
            return self.children[tab_id]

    notebook = Notebook()
    old_tabs = [Tab(notebook, name) for name in ("front", "next", "far")]
    notebook.children = {tab.name: tab for tab in old_tabs}

    SaadhyaDesktopApp._clear_notebook_tabs(notebook)

    assert notebook.tabs() == ()
    assert all(tab.destroyed for tab in old_tabs)


class FakeOptionTable:
    def __init__(self, selected="I001"):
        self.selected = selected
        self.rows = {selected: ["contract", "underlying", "expiry", "type", "strike", "premium", "entry", "target", "risk", "score", "fresh"]}
        self.tags = {}

    def selection(self):
        return (self.selected,) if self.selected else ()

    def item(self, item_id, option=None, **kwargs):
        if option == "values":
            return tuple(self.rows[item_id])
        if "values" in kwargs:
            self.rows[item_id] = list(kwargs["values"])
        if "tags" in kwargs:
            self.tags[item_id] = kwargs["tags"]


def test_option_selection_is_scoped_to_active_expiry_table():
    from app.gui.desktop import SaadhyaDesktopApp

    front = FakeOptionTable()
    far = FakeOptionTable()
    front_row = {
        "underlying": "NIFTY", "contract": "25000 CE", "expiry": "2026-09-10",
        "asset_class": "INDEX", "direction": "BUY", "score": 75,
        "market_regime": "NEUTRAL", "premium": "₹100.00", "entry": "₹90.00–₹110.00",
        "target": "₹150.00–₹200.00", "invalidation": "₹80.00", "warnings": [],
        "is_cached": False, "data_status": "fresh", "updated_at": "front-time",
    }
    far_row = {**front_row, "expiry": "2026-11-26", "updated_at": "far-time"}
    rendered = []
    app = SimpleNamespace(
        _option_rows_by_id={(front, "I001"): front_row, (far, "I001"): far_row},
        option_details=object(),
        _set_text=lambda _widget, content: rendered.append(content),
    )

    SaadhyaDesktopApp._show_selected_option(app, SimpleNamespace(widget=front))

    assert "2026-09-10" in rendered[0]
    assert "2026-11-26" not in rendered[0]


def test_failed_refresh_marks_visible_options_and_tracking_unavailable():
    from app.gui.desktop import SaadhyaDesktopApp

    table = FakeOptionTable()
    row = {"updated_at": "2026-09-08T12:00:00+00:00", "data_status": "fresh"}
    tracked = {
        "watchlist": [{
            "instrument_type": "OPTION", "underlying": "HAL",
            "expiry": "2026-09-24", "contract": "100 CE",
            "current_price": 10, "updated_at": "2026-09-08T12:00:00+00:00",
        }],
        "positions": [],
    }
    saved = []
    rendered = []
    app = SimpleNamespace(
        _option_rows_by_id={(table, "I001"): row}, _latest_quotes={"old": row},
        report={"generated_at": "2026-09-08T12:05:00+00:00"},
        tracking_data=tracked,
        tracking_store=SimpleNamespace(save=lambda data: saved.append(data)),
        _render_tracking=lambda: rendered.append(True),
    )

    SaadhyaDesktopApp._mark_latest_scan_unavailable(app)

    assert row["data_status"] == "unavailable"
    assert "UNAVAILABLE in latest scan" in table.rows["I001"][-1]
    assert table.tags["I001"] == ("unavailable",)
    assert app._latest_quotes == {}
    assert tracked["watchlist"][0]["quote_status"] == "UNAVAILABLE IN LATEST SCAN"
    assert saved and rendered


def test_overview_selection_uses_current_column_positions():
    from app.gui.desktop import SaadhyaDesktopApp

    table = FakeOptionTable()
    table.rows["I001"] = [
        1, "STOCK", "HAL.NS", "WATCH", "₹100.00", "₹98.00–₹102.00",
        "₹115.00", "+15.00%", 82, "MEDIUM", "NEUTRAL",
    ]
    rendered = []
    app = SimpleNamespace(
        table=table, opportunities=[],
        _set_details=lambda content: rendered.append(content),
    )

    SaadhyaDesktopApp._show_selected(app, None)

    assert "Projected ROI: +15.00%" in rendered[0]
    assert "Score: 82 | Risk: MEDIUM" in rendered[0]
    assert "News impact: NEUTRAL" in rendered[0]
