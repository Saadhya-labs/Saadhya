import ast
from pathlib import Path
import json

from app.gui.tracking import (
    LocalTrackingStore, contract_key, expiry_label, group_top_options, portfolio_state,
    quote_change, refresh_tracking_quotes,
)


def test_expiry_groups_rank_each_relative_expiry_independently():
    rows = [
        {
            "expiry": expiry,
            "expiry_rank": rank,
            "score": score,
            "underlying": underlying,
            "contract": f"{underlying}{score}",
        }
        for underlying, expiries in (
            ("NIFTY", ("2026-09-03", "2026-09-10", "2026-09-17")),
            ("HAL", ("2026-09-03", "2026-09-10", "2026-09-17")),
        )
        for rank, expiry in enumerate(expiries, 1)
        for score in range(6)
    ]
    grouped = group_top_options(rows)
    assert list(grouped) == [1, 2, 3]
    assert all(len(items) == 10 for items in grouped.values())
    assert all(item["expiry"] == "2026-09-17" for item in grouped[3])
    assert [item["score"] for item in grouped[1][:2]] == [5, 5]
    assert {item["underlying"] for item in grouped[1][:2]} == {"NIFTY", "HAL"}


def test_expiry_groups_infer_relative_buckets_for_divergent_legacy_calendars():
    rows = [
        {"expiry": expiry, "score": 50, "underlying": underlying, "contract": expiry}
        for underlying, expiries in (
            ("NIFTY", ("2026-09-17", "2026-09-24", "2026-10-01")),
            ("HAL", ("2026-09-24", "2026-10-29", "2026-11-26")),
        )
        for expiry in expiries
    ]

    grouped = group_top_options(rows)

    assert list(grouped) == [1, 2, 3]
    assert [
        {item["expiry"] for item in grouped[rank] if item["underlying"] == "HAL"}
        for rank in (1, 2, 3)
    ] == [{"2026-09-24"}, {"2026-10-29"}, {"2026-11-26"}]
    assert [
        {item["expiry"] for item in grouped[rank] if item["underlying"] == "NIFTY"}
        for rank in (1, 2, 3)
    ] == [{"2026-09-17"}, {"2026-09-24"}, {"2026-10-01"}]


def test_relative_expiry_labels_are_clear_while_exact_dates_remain_supported():
    assert [expiry_label(rank) for rank in (1, 2, 3)] == [
        "Front expiry", "Next expiry", "Far expiry",
    ]
    assert expiry_label("2026-09-24") == "24 Sep 2026"


def test_watchlist_calculation_and_persistence(tmp_path):
    store = LocalTrackingStore(tmp_path / "tracking.json")
    item = {
        "instrument_type": "OPTION", "underlying": "NIFTY", "expiry": "2026-09-10",
        "strike": 25000, "option_type": "CE", "contract": "25000 CE",
        "reference_price": 100, "current_price": 112.5,
    }
    store.upsert("watchlist", item)
    assert store.load()["watchlist"] == [item]
    assert quote_change(100, 112.5) == (12.5, 12.5)


def test_watchlist_selected_items_can_be_removed_and_stay_removed(tmp_path):
    store = LocalTrackingStore(tmp_path / "tracking.json")
    first = {
        "instrument_type": "OPTION", "underlying": "NIFTY", "expiry": "2026-09-24",
        "strike": 25000, "option_type": "CE", "contract": "25000 CE",
    }
    second = {
        "instrument_type": "OPTION", "underlying": "HAL", "expiry": "2026-09-24",
        "strike": 4500, "option_type": "PE", "contract": "4500 PE",
    }
    store.upsert("watchlist", first)
    store.upsert("watchlist", second)

    remaining = store.remove("watchlist", {contract_key(first)})

    assert remaining["watchlist"] == [second]
    assert store.load()["watchlist"] == [second]


def test_missing_quote_is_explicit_and_has_no_fabricated_change():
    assert quote_change(100, None) == (None, None)
    assert portfolio_state({"current_price": None}) == "WATCH — quote unavailable"


def test_portfolio_state_reuses_analysis_and_invalidation():
    assert portfolio_state({"current_price": 90, "invalidation_price": 95}) == "EXIT — invalidation reached"
    assert portfolio_state({"current_price": 105}, "BUY") == "HOLD"
    assert portfolio_state({"current_price": 105}, "SELL") == "EXIT — analysis weakened"


def test_desktop_has_no_order_execution_boundary():
    desktop_source = Path(__file__).resolve().parents[1] / "app/gui/desktop.py"
    tree = ast.parse(desktop_source.read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "place_order" not in called
    assert "place_trade" not in called


def test_corrupt_tracking_file_degrades_to_empty(tmp_path):
    path = tmp_path / "tracking.json"
    path.write_text("not json", encoding="utf-8")
    assert LocalTrackingStore(path).load() == {"watchlist": [], "positions": []}


def test_tracking_refresh_marks_missing_contract_without_advancing_old_quote():
    tracked = {
        "watchlist": [{
            "instrument_type": "OPTION", "underlying": "HAL",
            "expiry": "2026-09-10", "contract": "100 CE",
            "current_price": 12, "updated_at": "2026-09-08T12:00:00+00:00",
        }],
        "positions": [],
    }

    refresh_tracking_quotes(tracked, {}, "2026-09-08T12:05:00+00:00")

    assert tracked["watchlist"][0]["current_price"] == 12
    assert tracked["watchlist"][0]["updated_at"] == "2026-09-08T12:00:00+00:00"
    assert tracked["watchlist"][0]["quote_status"] == "UNAVAILABLE IN LATEST SCAN"


def test_legacy_watchlist_lot_backfills_from_exact_contract_without_changing_saved_price():
    tracked = {"watchlist": [{
        "instrument_type": "OPTION", "underlying": "NIFTY", "expiry": "2026-09-29",
        "contract": "21000 PE", "strike": 21000, "option_type": "PE",
        "reference_price": 76.30, "current_price": 70.45,
    }], "positions": []}
    lot_sizes = {("NIFTY", "2026-09-29", 21000, "PE"): 75}

    refresh_tracking_quotes(tracked, {}, lot_sizes=lot_sizes)

    item = tracked["watchlist"][0]
    assert item["reference_price"] == 76.30
    assert item["current_price"] == 70.45
    assert item["lot_size"] == 75
    assert item["one_lot_premium"] == 5722.50
    assert item["quote_status"] == "UNAVAILABLE IN LATEST SCAN"


def test_tracking_refresh_preserves_cached_quote_timestamp_and_marks_quality():
    tracked = {
        "watchlist": [{
            "instrument_type": "OPTION", "underlying": "HAL",
            "expiry": "2026-09-10", "contract": "100 CE",
        }],
        "positions": [],
    }
    quotes = {("HAL", "2026-09-10", "100 CE"): {
        "current_price": 12, "updated_at": "2026-09-08T11:50:00+00:00",
        "assessment": "FAVORABLE SETUP", "invalidation_price": 9,
        "is_cached": True,
    }}

    refresh_tracking_quotes(tracked, quotes, "2026-09-08T12:05:00+00:00")

    item = tracked["watchlist"][0]
    assert item["updated_at"] == "2026-09-08T11:50:00+00:00"
    assert item["quote_status"] == "STALE / CACHED"
    assert item["analysis_recommendation"] == "FAVORABLE SETUP"
