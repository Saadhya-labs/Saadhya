import queue
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_desktop_application_module_is_importable():
    from app.gui.desktop import SaadhyaDesktopApp
    from app.scanner.universe import NSE_STOCKS

    assert SaadhyaDesktopApp.__name__ == "SaadhyaDesktopApp"
    assert len(NSE_STOCKS) > 1


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


def test_kite_mode_requires_daily_connection_before_scan():
    from app.gui.desktop import SaadhyaDesktopApp

    app = SimpleNamespace(
        mode=Variable("kite"),
        kite_connected_on=None,
        scan_button=Button("disabled"),
        connect_button=Button("disabled"),
        connection=Variable(),
        status=Variable(),
    )

    SaadhyaDesktopApp._data_mode_changed(app)

    assert app.scan_button.state == "disabled"
    assert app.connect_button.state == "normal"
    assert app.connection.get() == "KITE NOT CONNECTED"
    assert "Connect to Kite" in app.status.get()

    source = (PROJECT_ROOT / "app/gui/desktop.py").read_text(encoding="utf-8")
    assert "KiteLogin" in source
    assert "connect_kite" in source


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
        "2 expiry levels per underlying  •  1 cached chain  •  1 unavailable chain"
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


def test_option_workspace_summary_uses_analyzed_chain_coverage():
    from app.gui.desktop import option_coverage_summary

    metadata = {"option_analysis": [
        {
            "underlying": "NIFTY", "status": "fresh",
            "expiries": ["2026-09-03", "2026-09-10", "2026-09-17"],
        },
        {
            "underlying": "HAL", "status": "cached",
            "expiries": ["2026-09-24", "2026-10-29", "2026-11-26"],
        },
        {"underlying": "TCS", "status": "unavailable", "expiries": []},
    ], "scan_failures": [{"symbol": "TCS", "source": "option-chain"}]}

    summary = option_coverage_summary([{"underlying": "NIFTY"}], metadata)

    assert summary == (
        "1 recommendation  •  2/3 chains analyzed (1 index, 1 stock)  •  "
        "3 expiry levels per underlying  •  1 cached chain  •  1 unavailable chain"
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
