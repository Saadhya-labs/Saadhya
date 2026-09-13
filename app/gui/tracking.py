"""Local, recommendation-only tracking models used by the desktop UI."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def contract_key(item):
    return "|".join(str(item.get(key, "")).upper() for key in (
        "instrument_type", "underlying", "expiry", "strike", "option_type"
    ))


def quote_change(reference_price, current_price):
    if reference_price in (None, 0) or current_price is None:
        return None, None
    change = float(current_price) - float(reference_price)
    return round(change, 2), round(change / float(reference_price) * 100, 2)


def group_top_options(rows, limit=10):
    """Rank contracts independently within the next three exact expiries."""
    selected_expiries = sorted({row["expiry"] for row in rows})[:3]
    result = {}
    for expiry in selected_expiries:
        candidates = sorted(
            (row for row in rows if row["expiry"] == expiry),
            key=lambda item: (-item["score"], item["underlying"], item["contract"]),
        )
        # One direction-aligned contract per underlying prevents CE/PE pairs
        # from crowding the cross-market ranking.
        unique = []
        seen_underlyings = set()
        for item in candidates:
            if item["underlying"] in seen_underlyings:
                continue
            seen_underlyings.add(item["underlying"])
            unique.append(item)
            if len(unique) == limit:
                break
        if unique:
            result[expiry] = unique
    return result


def expiry_label(expiry):
    try:
        parsed = datetime.strptime(expiry, "%Y-%m-%d")
        return parsed.strftime("%d %b %Y")
    except (TypeError, ValueError):
        return str(expiry)


def portfolio_state(item, recommendation=None):
    """Map existing analysis/risk output to a tracking state; never an order."""
    current = item.get("current_price")
    invalidation = item.get("invalidation_price")
    if current is None:
        return "WATCH — quote unavailable"
    if invalidation is not None and float(current) <= float(invalidation):
        return "EXIT — invalidation reached"
    normalized = str(recommendation or item.get("analysis_recommendation") or "").upper()
    if normalized in {"SELL", "STRONG SELL", "EXIT", "AVOID"}:
        return "EXIT — analysis weakened"
    if normalized in {"HOLD", "BUY", "STRONG BUY", "FAVORABLE RISK/REWARD"}:
        return "HOLD"
    return "WATCH"


def display_price(value):
    return "Quote unavailable" if value is None else f"₹{float(value):.2f}"


def refresh_tracking_quotes(tracking_data, quotes, generated_at=None):
    """Merge only quotes observed in the current scan into local tracking.

    Missing contracts retain their last known price and timestamp, but are
    explicitly marked unavailable. Cached contracts retain the provider's
    original quote timestamp so a reconnect cannot make old data look fresh.
    """
    for collection in ("watchlist", "positions"):
        for item in tracking_data[collection]:
            if item.get("instrument_type") != "OPTION":
                continue
            key = (
                item.get("underlying", ""),
                item.get("expiry", ""),
                str(item.get("contract", "")),
            )
            quote = quotes.get(key)
            if quote is None:
                item["quote_status"] = "UNAVAILABLE IN LATEST SCAN"
                continue

            is_cached = bool(quote.get("is_cached"))
            item["current_price"] = quote["current_price"]
            quote_timestamp = quote.get("updated_at")
            if quote_timestamp:
                item["updated_at"] = quote_timestamp
            elif not is_cached and generated_at:
                item["updated_at"] = generated_at
            item["analysis_recommendation"] = quote.get("assessment")
            item["invalidation_price"] = quote.get("invalidation_price")
            item["quote_status"] = "STALE / CACHED" if is_cached else "FRESH"
    return tracking_data


class LocalTrackingStore:
    """Small JSON store. Corrupt/missing data degrades to empty collections."""

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            data = {}
        return {"watchlist": list(data.get("watchlist", [])), "positions": list(data.get("positions", []))}

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def upsert(self, collection, item):
        data = self.load()
        key = contract_key(item)
        values = data[collection]
        for index, existing in enumerate(values):
            if contract_key(existing) == key:
                values[index] = {**existing, **item}
                break
        else:
            values.append(item)
        self.save(data)
        return data

    def remove(self, collection, keys):
        """Remove selected locally tracked instruments by their stable keys."""
        data = self.load()
        selected = set(keys)
        data[collection] = [
            item for item in data[collection]
            if contract_key(item) not in selected
        ]
        self.save(data)
        return data
