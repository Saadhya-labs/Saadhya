from datetime import datetime, timedelta, timezone

import pytest
import requests

from app.data.providers.kite_stock_provider import KiteConfigurationError, KiteStockProvider


class Response:
    def __init__(self, text="", payload=None):
        self.text = text
        self.payload = payload or {}

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class Session:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if url.endswith("/instruments/NSE"):
            return Response("instrument_token,tradingsymbol,instrument_type\n123,HAL,EQ\n")
        if "/historical/123/day" in url:
            return Response(payload={"data": {"candles": [["2026-01-01T00:00:00+0530", 1, 3, 1, 2, 50]]}})
        return Response(payload={"data": {"NSE:HAL": {"last_price": 123.45}}})


def test_kite_provider_requires_local_credentials():
    with pytest.raises(KiteConfigurationError):
        KiteStockProvider()


def test_kite_provider_uses_read_only_market_endpoints(tmp_path):
    session = Session()
    provider = KiteStockProvider(
        "key", "token", session=session,
        now=lambda: datetime(2026, 2, 1, tzinfo=timezone.utc),
        history_cache_dir=tmp_path,
    )

    history = provider.get_history("HAL.NS")

    assert list(history.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert provider.get_price("HAL.NS") == 123.45
    assert all("/orders" not in call[0] for call in session.calls)


def test_kite_provider_reuses_last_history_during_reconnect(tmp_path):
    session = Session()
    clock = [datetime(2026, 2, 1, tzinfo=timezone.utc)]
    provider = KiteStockProvider(
        "key", "token", session=session, retries=1,
        now=lambda: clock[0],
        history_cache_dir=tmp_path,
    )
    first = provider.get_history("HAL.NS")
    clock[0] += timedelta(hours=7)

    original_get = session.get

    def disconnected(url, **kwargs):
        if "/historical/" in url:
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected
    cached = provider.get_history("HAL.NS")

    assert cached.equals(first)
    assert provider.stale_symbols == {"HAL.NS"}


def test_kite_provider_reuses_fresh_history_without_network_request(tmp_path):
    session = Session()
    clock = [datetime(2026, 2, 1, tzinfo=timezone.utc)]
    provider = KiteStockProvider(
        "key", "token", session=session, now=lambda: clock[0],
        history_cache_dir=tmp_path,
    )

    first = provider.get_history("HAL.NS")
    historical_calls = lambda: sum("/historical/" in url for url, _ in session.calls)
    assert historical_calls() == 1

    clock[0] += timedelta(minutes=4)
    second = provider.get_history("HAL.NS")

    assert second.equals(first)
    assert historical_calls() == 1


def test_kite_history_cache_survives_provider_restart(tmp_path):
    clock = [datetime(2026, 2, 1, tzinfo=timezone.utc)]
    first_session = Session()
    first_provider = KiteStockProvider(
        "key", "token", session=first_session, now=lambda: clock[0],
        history_cache_dir=tmp_path,
    )
    expected = first_provider.get_history("HAL.NS")

    second_session = Session()
    second_provider = KiteStockProvider(
        "key", "token", session=second_session, now=lambda: clock[0],
        history_cache_dir=tmp_path,
    )
    actual = second_provider.get_history("HAL.NS")

    assert list(actual.columns) == list(expected.columns)
    assert actual.to_numpy().tolist() == expected.to_numpy().tolist()
    assert not any("/historical/" in url for url, _ in second_session.calls)


def test_kite_history_cache_rejects_future_timestamp(tmp_path):
    future_session = Session()
    future_provider = KiteStockProvider(
        "key", "token", session=future_session,
        now=lambda: datetime(2026, 2, 2, tzinfo=timezone.utc),
        history_cache_dir=tmp_path,
    )
    future_provider.get_history("HAL.NS")

    current_session = Session()
    current_provider = KiteStockProvider(
        "key", "token", session=current_session,
        now=lambda: datetime(2026, 2, 1, tzinfo=timezone.utc),
        history_cache_dir=tmp_path,
    )

    current_provider.get_history("HAL.NS")

    assert sum("/historical/" in url for url, _ in current_session.calls) == 1


def test_kite_provider_refreshes_instrument_master_after_date_rollover(tmp_path):
    session = Session()
    clock = [datetime(2026, 2, 1, tzinfo=timezone.utc)]
    provider = KiteStockProvider(
        "key", "token", session=session, now=lambda: clock[0],
        history_cache_dir=tmp_path,
    )

    provider.available_nse_equities()
    provider.available_nse_equities()
    instrument_calls = lambda: sum(
        url.endswith("/instruments/NSE") for url, _ in session.calls
    )
    assert instrument_calls() == 1

    clock[0] += timedelta(days=1)
    provider.available_nse_equities()

    assert instrument_calls() == 2


def test_kite_provider_keeps_last_instrument_master_and_retries_malformed_rollover(tmp_path):
    class RolloverSession(Session):
        instrument_text = "instrument_token,tradingsymbol,instrument_type\n123,HAL,EQ\n"

        def get(self, url, **kwargs):
            if url.endswith("/instruments/NSE"):
                self.calls.append((url, kwargs))
                return Response(self.instrument_text)
            return super().get(url, **kwargs)

    session = RolloverSession()
    clock = [datetime(2026, 2, 1, tzinfo=timezone.utc)]
    provider = KiteStockProvider(
        "key", "token", session=session, now=lambda: clock[0],
        history_cache_dir=tmp_path,
    )
    assert provider.available_nse_equities() == ("HAL.NS",)

    clock[0] += timedelta(days=1)
    session.instrument_text = "temporarily unavailable"
    assert provider.available_nse_equities() == ("HAL.NS",)
    assert provider.instrument_master_stale is True
    assert "malformed NSE instrument master" in provider.instrument_master_error

    session.instrument_text = "instrument_token,tradingsymbol,instrument_type\n456,TCS,EQ\n"
    assert provider.available_nse_equities() == ("TCS.NS",)
    assert provider.instrument_master_stale is False
    assert provider.instrument_master_error is None
