from datetime import date, datetime, timezone
import pytest
import requests

from app.data.providers.kite_option_provider import KiteOptionProvider


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
        self.quote_calls = []

    def get(self, url, **kwargs):
        if url.endswith("/instruments"):
            return Response(
                "exchange,tradingsymbol,name,expiry,strike,instrument_type,lot_size\n"
                "NFO,HAL26SEP100CE,HAL,2026-09-24,100,CE,75\n"
                "NFO,HAL26SEP100PE,HAL,2026-09-24,100,PE,75\n"
            )
        if url.endswith("/quote/ltp"):
            return Response(payload={"data": {"NSE:HAL": {"last_price": 101}}})
        self.quote_calls.append(kwargs.get("params", []))
        return Response(payload={"data": {
            "NFO:HAL26SEP100CE": {"last_price": 6, "volume": 900000, "oi": 1500000},
            "NFO:HAL26SEP100PE": {"last_price": 4, "volume": 800000, "oi": 1200000},
        }})


def test_kite_option_provider_returns_near_expiry_read_only_quotes():
    provider = KiteOptionProvider(
        "key", "token", session=Session(), today=lambda: date(2026, 8, 1)
    )

    options = provider.get_option_chain("HAL.NS")

    assert [option.option_type for option in options] == ["CE", "PE"]
    assert options[0].premium == 6.0
    assert options[0].lot_size == 75
    assert options[0].one_lot_premium == 450.0
    assert options[0].delta == 0.0


def test_saved_watchlist_lot_lookup_requires_exact_expiry_strike_and_side():
    provider = KiteOptionProvider("key", "token", session=Session())
    provider._instruments = [{
        "exchange": "NFO", "name": "NIFTY", "expiry": "2026-09-29",
        "strike": "21000", "instrument_type": "PE", "lot_size": "75",
    }]
    saved = [
        ("NIFTY", "2026-09-29", 21000, "PE"),
        ("NIFTY", "2026-09-29", 21000, "CE"),
        ("NIFTY", "2026-10-29", 21000, "PE"),
    ]
    assert provider.lot_sizes_for_contracts(saved) == {saved[0]: 75}


class LargeChainSession:
    def __init__(self):
        self.quote_batch_sizes = []

    def get(self, url, **kwargs):
        if url.endswith("/instruments"):
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            rows.extend(
                f"NFO,NIFTY26SEPC{strike},NIFTY,2026-09-24,{strike},CE"
                for strike in range(401)
            )
            return Response("\n".join(rows) + "\n")
        params = kwargs.get("params", [])
        if url.endswith("/quote/ltp"):
            return Response(payload={"data": {"NSE:NIFTY 50": {"last_price": 200}}})
        self.quote_batch_sizes.append(len(params))
        return Response(payload={"data": {
            value: {"last_price": 1, "volume": 1, "oi": 1}
            for _, value in params
        }})


def test_kite_option_provider_batches_full_chain_and_supports_index_underlying():
    session = LargeChainSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 8, 1)
    )

    options = provider.get_option_chain("NIFTY")

    assert len(options) == 401
    assert session.quote_batch_sizes == [400, 1]
    assert provider.available_fno_underlyings() == ("NIFTY",)


class FullUniverseSession:
    def __init__(self):
        self.quote_batch_sizes = []

    def get(self, url, **kwargs):
        if url.endswith("/instruments"):
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            for underlying in ("HAL", "TCS"):
                for expiry_number, expiry in enumerate(
                    ("2026-09-24", "2026-10-29", "2026-11-26")
                ):
                    rows.extend(
                        f"NFO,{underlying}{expiry_number}C{strike},{underlying},{expiry},{strike},CE"
                        for strike in range(67)
                    )
            return Response("\n".join(rows) + "\n")
        params = kwargs.get("params", [])
        self.quote_batch_sizes.append(len(params))
        return Response(payload={"data": {
            value: {"last_price": 1, "volume": 1, "oi": 1}
            for _, value in params
        }})


def test_kite_option_provider_batches_quotes_across_full_fno_universe():
    session = FullUniverseSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1)
    )

    chains = provider.get_option_chains(("HAL.NS", "TCS"))

    assert session.quote_batch_sizes == [400, 2]
    assert set(chains) == {"HAL", "TCS"}
    assert len(chains["HAL"]) == 201
    assert {option.expiry for option in chains["TCS"]} == {
        "2026-09-24", "2026-10-29", "2026-11-26"
    }


def test_kite_option_provider_keeps_full_universe_when_rollover_master_is_truncated():
    class RolloverSession:
        names = ("HAL", "TCS", "NIFTY")

        def get(self, url, **_kwargs):
            assert url.endswith("/instruments")
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            rows.extend(
                f"NFO,{name}26SEPCE,{name},2026-09-24,100,CE"
                for name in self.names
            )
            return Response("\n".join(rows) + "\n")

    session = RolloverSession()
    clock = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: clock[0], retries=1
    )
    assert provider.available_fno_underlyings() == ("HAL", "NIFTY", "TCS")

    clock[0] = date(2026, 9, 2)
    session.names = ("HAL",)
    assert provider.available_fno_underlyings() == ("HAL", "NIFTY", "TCS")
    assert provider.instrument_master_stale is True
    assert "truncated" in provider.instrument_master_error

    session.names = ("HAL", "TCS", "NIFTY", "INFY")
    assert provider.available_fno_underlyings() == ("HAL", "INFY", "NIFTY", "TCS")
    assert provider.instrument_master_stale is False


def test_kite_option_provider_rejects_partially_malformed_initial_master():
    class MalformedSession:
        def get(self, url, **_kwargs):
            assert url.endswith("/instruments")
            return Response(
                "exchange,tradingsymbol,name,expiry,strike,instrument_type\n"
                "NFO,HAL26SEP100CE,HAL,2026-09-24,100,CE\n"
                "NFO,TCS26SEPCE,TCS,not-a-date,invalid,CE\n"
            )

    provider = KiteOptionProvider(
        "key", "token", session=MalformedSession(),
        today=lambda: date(2026, 9, 1), retries=1,
    )

    with pytest.raises(ValueError, match="malformed contracts"):
        provider.available_fno_underlyings()


def test_kite_option_provider_keeps_last_master_when_refresh_has_malformed_row():
    class RolloverSession:
        malformed = False

        def get(self, url, **_kwargs):
            assert url.endswith("/instruments")
            second = (
                "NFO,TCS26SEPCE,TCS,2026-09-24,not-a-number,CE\n"
                if self.malformed else
                "NFO,TCS26SEP100CE,TCS,2026-09-24,100,CE\n"
            )
            return Response(
                "exchange,tradingsymbol,name,expiry,strike,instrument_type\n"
                "NFO,HAL26SEP100CE,HAL,2026-09-24,100,CE\n" + second
            )

    session = RolloverSession()
    current_day = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session,
        today=lambda: current_day[0], retries=1,
    )
    assert provider.available_fno_underlyings() == ("HAL", "TCS")

    current_day[0] = date(2026, 9, 2)
    session.malformed = True

    assert provider.available_fno_underlyings() == ("HAL", "TCS")
    assert provider.instrument_master_stale is True
    assert "malformed contracts" in provider.instrument_master_error


def test_kite_option_provider_rejects_missing_strikes_with_names_intact():
    class RolloverSession:
        strikes = range(5)

        def get(self, url, **_kwargs):
            assert url.endswith("/instruments")
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            rows.extend(
                f"NFO,{name}26SEP{strike}CE,{name},2026-09-24,{strike},CE"
                for name in ("HAL", "TCS") for strike in self.strikes
            )
            return Response("\n".join(rows) + "\n")

    session = RolloverSession()
    current_day = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0], retries=1
    )
    assert len(provider._load_instruments()) == 10

    current_day[0] = date(2026, 9, 2)
    session.strikes = range(2)
    assert len(provider._load_instruments()) == 10
    assert provider.instrument_master_stale is True
    assert "truncated" in provider.instrument_master_error

    session.strikes = range(6)
    assert len(provider._load_instruments()) == 12
    assert provider.instrument_master_stale is False


def test_kite_option_provider_rejects_one_damaged_chain_in_large_master():
    class RolloverSession:
        truncated_underlying = None

        def get(self, url, **_kwargs):
            assert url.endswith("/instruments")
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            for name in ("HAL", "TCS", "INFY", "RELIANCE", "SBIN"):
                expiries = (
                    ("2026-09-24", "2026-10-29")
                    if name == self.truncated_underlying
                    else ("2026-09-24", "2026-10-29", "2026-11-26")
                )
                for expiry_number, expiry in enumerate(expiries):
                    rows.extend(
                        f"NFO,{name}{expiry_number}{strike}CE,{name},{expiry},{strike},CE"
                        for strike in range(4)
                    )
            return Response("\n".join(rows) + "\n")

    session = RolloverSession()
    current_day = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0], retries=1
    )
    assert len(provider._load_instruments()) == 60

    current_day[0] = date(2026, 9, 2)
    session.truncated_underlying = "HAL"
    assert len(provider._load_instruments()) == 60
    assert provider.instrument_master_stale is True
    assert "for HAL" in provider.instrument_master_error

    session.truncated_underlying = None
    assert len(provider._load_instruments()) == 60
    assert provider.instrument_master_stale is False


def test_kite_option_provider_allows_expired_contracts_to_roll_off():
    class RolloverSession:
        include_expired = True

        def get(self, url, **_kwargs):
            assert url.endswith("/instruments")
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            if self.include_expired:
                rows.extend(
                    f"NFO,HAL26SEP{strike}CE,HAL,2026-09-01,{strike},CE"
                    for strike in range(8)
                )
            rows.extend(
                f"NFO,HAL26OCT{strike}CE,HAL,2026-10-29,{strike},CE"
                for strike in range(2)
            )
            return Response("\n".join(rows) + "\n")

    session = RolloverSession()
    current_day = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0], retries=1
    )
    assert len(provider._load_instruments()) == 10

    current_day[0] = date(2026, 9, 2)
    session.include_expired = False
    assert len(provider._load_instruments()) == 2
    assert provider.instrument_master_stale is False


def test_kite_option_provider_selects_monthly_not_weekly_index_expiries():
    provider = KiteOptionProvider(
        "key", "token", session=Session(), today=lambda: date(2026, 9, 1)
    )
    rows = [
        {
            "exchange": "NFO", "tradingsymbol": f"NIFTY{expiry}CE",
            "name": "NIFTY", "expiry": expiry, "strike": "25000",
            "instrument_type": "CE",
        }
        for expiry in (
            "2026-09-08", "2026-09-15", "2026-09-22", "2026-09-29",
            "2026-10-06", "2026-10-27", "2026-11-24",
        )
    ]
    selected = provider._selected_contracts("NIFTY", rows)
    assert {row["expiry"] for row in selected} == {
        "2026-09-29", "2026-10-27", "2026-11-24",
    }


def test_kite_option_provider_reuses_batched_chains_during_reconnect():
    session = FullUniverseSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )
    first = provider.get_option_chains(("HAL", "TCS"))
    original_get = session.get

    def disconnected(url, **kwargs):
        if url.endswith("/quote"):
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected
    cached = provider.get_option_chains(("HAL", "TCS"))

    assert [item.premium for item in cached["HAL"]] == [
        item.premium for item in first["HAL"]
    ]
    assert provider.stale_symbols == {"HAL", "TCS"}


def test_kite_option_provider_retains_original_timestamp_for_cached_chain():
    session = Session()
    moments = iter((
        datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc),
        datetime(2026, 9, 8, 12, 5, tzinfo=timezone.utc),
    ))
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 8, 1),
        now=lambda: next(moments), retries=1,
    )
    provider.get_option_chain("HAL")
    original_timestamp = provider.chain_updated_at["HAL"]
    original_get = session.get

    def disconnected(url, **kwargs):
        if url.endswith("/quote"):
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected
    provider.get_option_chain("HAL")

    assert provider.chain_updated_at["HAL"] == original_timestamp
    assert original_timestamp == "2026-09-08T12:00:00+00:00"


def test_kite_option_provider_reuses_last_chain_during_reconnect():
    session = Session()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 8, 1), retries=1
    )
    first = provider.get_option_chain("HAL")

    original_get = session.get

    def disconnected(url, **kwargs):
        if url.endswith("/quote"):
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected
    cached = provider.get_option_chain("HAL")

    assert [option.premium for option in cached] == [option.premium for option in first]
    assert provider.stale_symbols == {"HAL"}


class PartiallyDisconnectedSession:
    def __init__(self):
        self.quote_call = 0
        self.disconnect_hal = False

    def get(self, url, **kwargs):
        if url.endswith("/instruments"):
            rows = ["exchange,tradingsymbol,name,expiry,strike,instrument_type"]
            rows.extend(
                f"NFO,HALC{strike},HAL,2026-09-24,{strike},CE"
                for strike in range(400)
            )
            rows.extend(
                f"NFO,TCSC{strike},TCS,2026-09-24,{strike},CE"
                for strike in range(2)
            )
            return Response("\n".join(rows) + "\n")

        params = kwargs.get("params", [])
        self.quote_call += 1
        if self.disconnect_hal and len(params) == 400:
            raise requests.ConnectionError("HAL batch offline")
        return Response(payload={"data": {
            value: {"last_price": self.quote_call, "volume": 1, "oi": 1}
            for _, value in params
        }})


def test_kite_option_provider_keeps_other_batches_fresh_during_partial_disconnect():
    session = PartiallyDisconnectedSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )
    initial = provider.get_option_chains(("HAL", "TCS"))
    initial_tcs_premium = initial["TCS"][0].premium

    session.disconnect_hal = True
    refreshed = provider.get_option_chains(("HAL", "TCS"))

    assert refreshed["HAL"][0].premium == initial["HAL"][0].premium
    assert refreshed["TCS"][0].premium != initial_tcs_premium
    assert provider.stale_symbols == {"HAL"}
    assert provider.chain_failures == {}


class IncompleteQuoteSession:
    def __init__(self):
        self.quote_call = 0
        self.omit_one = False
        self.bad_price = False

    def get(self, url, **kwargs):
        if url.endswith("/instruments"):
            return Response(
                "exchange,tradingsymbol,name,expiry,strike,instrument_type\n"
                "NFO,HAL100CE,HAL,2026-09-24,100,CE\n"
                "NFO,HAL100PE,HAL,2026-09-24,100,PE\n"
            )

        self.quote_call += 1
        keys = [value for _, value in kwargs.get("params", [])]
        if self.omit_one:
            keys = keys[:-1]
        data = {
            key: {"last_price": self.quote_call, "volume": 1, "oi": 1}
            for key in keys
        }
        if self.bad_price:
            data[keys[-1]]["last_price"] = "not-a-price"
        return Response(payload={"data": data})


def test_kite_option_provider_rejects_silently_incomplete_chain_and_uses_cache():
    session = IncompleteQuoteSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )
    initial = provider.get_option_chains(("HAL",))

    session.omit_one = True
    refreshed = provider.get_option_chains(("HAL",))

    assert len(refreshed["HAL"]) == 2
    assert refreshed["HAL"][0].premium == initial["HAL"][0].premium
    assert provider.stale_symbols == {"HAL"}
    assert provider.chain_failures == {}


def test_kite_option_provider_reports_incomplete_chain_without_cache():
    session = IncompleteQuoteSession()
    session.omit_one = True
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )

    chains = provider.get_option_chains(("HAL",))

    assert chains == {}
    assert "1 quote(s) missing" in provider.chain_failures["HAL"]


def test_single_chain_fetch_uses_cache_when_response_is_incomplete():
    session = IncompleteQuoteSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )
    initial = provider.get_option_chain("HAL")

    session.omit_one = True
    refreshed = provider.get_option_chain("HAL")

    assert len(refreshed) == 2
    assert refreshed[0].premium == initial[0].premium
    assert provider.stale_symbols == {"HAL"}


def test_batched_fetch_uses_complete_cache_when_quote_price_is_unusable():
    session = IncompleteQuoteSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )
    initial = provider.get_option_chains(("HAL",))["HAL"]

    session.bad_price = True
    refreshed = provider.get_option_chains(("HAL",))

    assert [item.premium for item in refreshed["HAL"]] == [item.premium for item in initial]
    assert provider.stale_symbols == {"HAL"}


def test_unusable_quote_without_cache_reports_unavailable_chain():
    session = IncompleteQuoteSession()
    session.bad_price = True
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )

    assert provider.get_option_chains(("HAL",)) == {}
    assert "1 quote(s) unusable" in provider.chain_failures["HAL"]


def test_single_chain_fetch_uses_cache_when_quote_price_is_unusable():
    session = IncompleteQuoteSession()
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: date(2026, 9, 1), retries=1
    )
    initial = provider.get_option_chain("HAL")

    session.bad_price = True
    refreshed = provider.get_option_chain("HAL")

    assert [item.premium for item in refreshed] == [item.premium for item in initial]
    assert provider.stale_symbols == {"HAL"}


def test_batched_reconnect_never_republishes_expired_cached_contracts():
    session = FullUniverseSession()
    current_day = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0], retries=1
    )
    provider.get_option_chains(("HAL",))
    current_day[0] = date(2026, 10, 1)
    original_get = session.get

    def disconnected(url, **kwargs):
        if url.endswith("/quote"):
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected
    cached = provider.get_option_chains(("HAL",))

    assert {contract.expiry for contract in cached["HAL"]} == {
        "2026-10-29", "2026-11-26",
    }
    assert provider.stale_symbols == {"HAL"}


def test_batched_reconnect_marks_fully_expired_cache_unavailable():
    session = Session()
    current_day = [date(2026, 8, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0], retries=1
    )
    provider.get_option_chains(("HAL",))
    current_day[0] = date(2026, 10, 1)
    original_get = session.get

    def disconnected(url, **kwargs):
        if url.endswith("/quote"):
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected
    cached = provider.get_option_chains(("HAL",))

    assert cached == {}
    assert provider.stale_symbols == set()
    assert "No unexpired last-known-good contracts remain" in provider.chain_failures["HAL"]


def test_single_chain_reconnect_rejects_fully_expired_cache():
    session = Session()
    current_day = [date(2026, 8, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0], retries=1
    )
    provider.get_option_chain("HAL")
    current_day[0] = date(2026, 10, 1)
    original_get = session.get

    def disconnected(url, **kwargs):
        if url.endswith("/quote"):
            raise requests.ConnectionError("offline")
        return original_get(url, **kwargs)

    session.get = disconnected

    with pytest.raises(RuntimeError, match="No unexpired last-known-good contracts remain"):
        provider.get_option_chain("HAL")

    assert provider.stale_symbols == set()


class DailyInstrumentSession(Session):
    def __init__(self):
        super().__init__()
        self.instrument_calls = 0

    def get(self, url, **kwargs):
        if url.endswith("/instruments"):
            self.instrument_calls += 1
        return super().get(url, **kwargs)


def test_kite_option_provider_refreshes_instrument_master_after_date_rollover():
    session = DailyInstrumentSession()
    current_day = [date(2026, 8, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0]
    )

    provider.available_fno_underlyings()
    provider.available_fno_underlyings()
    assert session.instrument_calls == 1

    current_day[0] = date(2026, 8, 2)
    provider.available_fno_underlyings()

    assert session.instrument_calls == 2


def test_kite_option_provider_keeps_last_master_and_retries_malformed_rollover():
    class RolloverSession(Session):
        instrument_text = (
            "exchange,tradingsymbol,name,expiry,strike,instrument_type\n"
            "NFO,HAL26SEP100CE,HAL,2026-09-24,100,CE\n"
        )

        def get(self, url, **kwargs):
            if url.endswith("/instruments"):
                return Response(self.instrument_text)
            return super().get(url, **kwargs)

    session = RolloverSession()
    current_day = [date(2026, 9, 1)]
    provider = KiteOptionProvider(
        "key", "token", session=session, today=lambda: current_day[0]
    )
    assert provider.available_fno_underlyings() == ("HAL",)

    current_day[0] = date(2026, 9, 2)
    session.instrument_text = "temporarily unavailable"
    assert provider.available_fno_underlyings() == ("HAL",)
    assert provider.instrument_master_stale is True
    assert "malformed option instrument master" in provider.instrument_master_error

    session.instrument_text = (
        "exchange,tradingsymbol,name,expiry,strike,instrument_type\n"
        "NFO,TCS26SEP100CE,TCS,2026-09-24,100,CE\n"
    )
    assert provider.available_fno_underlyings() == ("TCS",)
    assert provider.instrument_master_stale is False
    assert provider.instrument_master_error is None
