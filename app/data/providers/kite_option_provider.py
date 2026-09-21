"""Read-only NFO option-chain adapter backed by Kite Connect market data."""

from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from io import StringIO
import math
import time

import requests

from app.data.providers.option_provider import OptionDataProvider
from app.data.providers.kite_stock_provider import KiteConfigurationError
from app.options.models import OptionContract


class KiteOptionProvider(OptionDataProvider):
    """Build an actionable near-expiry option set using Kite NFO quotes.

    Kite's quote response does not contain exchange-supplied implied volatility
    or Greeks, so they are deliberately left as unavailable rather than guessed.
    """

    API_ROOT = "https://api.kite.trade"
    QUOTE_BATCH_SIZE = 400
    INDEX_SPOT_SYMBOLS = {
        "NIFTY": "NSE:NIFTY 50",
        "BANKNIFTY": "NSE:NIFTY BANK",
        "FINNIFTY": "NSE:NIFTY FIN SERVICE",
        "MIDCPNIFTY": "NSE:NIFTY MID SELECT",
        "SENSEX": "BSE:SENSEX",
        "BANKEX": "BSE:BANKEX",
    }

    def __init__(
        self,
        api_key=None,
        access_token=None,
        session=None,
        today=None,
        retries=3,
        now=None,
    ):
        if not api_key or not access_token:
            raise KiteConfigurationError(
                "Kite option data requires KITE_API_KEY and a current KITE_ACCESS_TOKEN."
            )
        self.api_key = api_key
        self.access_token = access_token
        self.session = session or requests.Session()
        self._today = today or date.today
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._instruments = None
        self._instruments_date = None
        self.instrument_master_stale = False
        self.instrument_master_error = None
        self.retries = max(1, retries)
        self._last_chains = {}
        self.stale_symbols = set()
        self.chain_failures = {}
        self.chain_updated_at = {}

    @property
    def headers(self):
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}",
        }

    @staticmethod
    def _underlying(symbol):
        return symbol.upper().replace(".NS", "").replace("NSE:", "")

    def _get(self, path, **kwargs):
        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(
                    f"{self.API_ROOT}{path}", headers=self.headers, timeout=20, **kwargs
                )
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(0.25 * (2**attempt))
        raise RuntimeError(f"Kite option data is temporarily unavailable: {last_error}") from last_error

    @staticmethod
    def _validate_option_instrument_master(instruments):
        """Reject a successful download containing malformed option contracts.

        The all-instruments endpoint also contains cash, futures, currency, and
        commodity rows, so only NSE/BSE option records belong to this check.
        A single malformed option row can otherwise fail quote planning after
        the new master has already replaced the last-known-good copy.
        """
        option_rows = [
            row for row in instruments
            if row.get("exchange") in {"NFO", "BFO"}
            and row.get("instrument_type") in {"CE", "PE"}
        ]
        if not option_rows:
            raise ValueError("Kite returned an empty or malformed option instrument master.")

        for row in option_rows:
            if not row.get("tradingsymbol") or not row.get("name") or not row.get("expiry"):
                raise ValueError(
                    "Kite returned an option instrument master with incomplete contracts."
                )
            try:
                date.fromisoformat(row["expiry"])
                strike = float(row["strike"])
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    "Kite returned an option instrument master with malformed contracts."
                ) from exc
            if not math.isfinite(strike) or strike < 0:
                raise ValueError(
                    "Kite returned an option instrument master with malformed contracts."
                )

        return option_rows

    def _load_instruments(self):
        current_date = self._today()
        if self._instruments is None or self._instruments_date != current_date:
            try:
                instruments = list(
                    csv.DictReader(StringIO(self._get("/instruments").text))
                )
                self._validate_option_instrument_master(instruments)
                if self._instruments is not None:
                    previous = {
                        row.get("name") for row in self._instruments
                        if row.get("exchange") == "NFO"
                        and row.get("instrument_type") in {"CE", "PE"}
                        and row.get("tradingsymbol")
                        and row.get("expiry")
                        and row.get("name")
                    }
                    current = {
                        row.get("name") for row in instruments
                        if row.get("exchange") == "NFO"
                        and row.get("instrument_type") in {"CE", "PE"}
                        and row.get("tradingsymbol")
                        and row.get("expiry")
                        and row.get("name")
                    }
                    if previous and len(current) < len(previous) * 0.8:
                        raise ValueError(
                            "Kite returned a truncated option instrument master."
                        )
                    # Names alone do not catch a master that retains every
                    # underlying but drops most strikes or expiries. Compare
                    # only contracts still live today so a normal expiry
                    # rollover does not look like a truncated download.
                    def live_contracts_by_underlying(rows):
                        contracts = {}
                        for row in rows:
                            if (
                                row.get("exchange") not in {"NFO", "BFO"}
                                or row.get("instrument_type") not in {"CE", "PE"}
                                or not row.get("tradingsymbol")
                                or not row.get("name")
                                or row.get("expiry", "") < current_date.isoformat()
                            ):
                                continue
                            contracts.setdefault(row["name"], set()).add(
                                (row["exchange"], row["tradingsymbol"])
                            )
                        return contracts

                    previous_by_underlying = live_contracts_by_underlying(
                        self._instruments
                    )
                    current_by_underlying = live_contracts_by_underlying(instruments)
                    previous_contracts = set().union(
                        *previous_by_underlying.values()
                    ) if previous_by_underlying else set()
                    current_contracts = set().union(
                        *current_by_underlying.values()
                    ) if current_by_underlying else set()
                    if previous_contracts and len(current_contracts) < len(previous_contracts) * 0.8:
                        raise ValueError(
                            "Kite returned a truncated option instrument master."
                        )
                    # A full-universe count can hide a damaged chain for one
                    # underlying when every other chain is intact. Validate
                    # each still-live chain independently so a missing future
                    # expiry or strike set cannot look like fresh coverage.
                    for underlying, previous_chain in previous_by_underlying.items():
                        # A whole underlying can leave the derivative universe;
                        # the aggregate name guard handles suspicious mass loss.
                        # This check targets retained but partially downloaded
                        # chains, which are otherwise hidden by universe totals.
                        if underlying not in current_by_underlying:
                            continue
                        current_chain = current_by_underlying[underlying]
                        if len(current_chain) < len(previous_chain) * 0.8:
                            raise ValueError(
                                "Kite returned a truncated option instrument master "
                                f"for {underlying}."
                            )
            except (RuntimeError, requests.RequestException, ValueError) as exc:
                if self._instruments is None:
                    raise
                # Keep the last complete master available across a rollover
                # disconnect. The old date deliberately remains unchanged so
                # the next auto-refresh retries the daily master download.
                self.instrument_master_stale = True
                self.instrument_master_error = str(exc)
                return self._instruments

            self._instruments = instruments
            self._instruments_date = current_date
            self.instrument_master_stale = False
            self.instrument_master_error = None
        return self._instruments

    def _quote(self, instruments):
        quotes = {}
        for start in range(0, len(instruments), self.QUOTE_BATCH_SIZE):
            batch = instruments[start:start + self.QUOTE_BATCH_SIZE]
            response = self._get("/quote", params=[("i", item) for item in batch])
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else None
            if not isinstance(data, dict):
                raise ValueError("Kite returned a malformed option quote response.")
            quotes.update(data)
        return quotes

    def _quote_resilient(self, instruments):
        """Fetch independent quote batches and retain successful responses."""
        quotes = {}
        failures = []
        for start in range(0, len(instruments), self.QUOTE_BATCH_SIZE):
            batch = instruments[start:start + self.QUOTE_BATCH_SIZE]
            try:
                response = self._get("/quote", params=[("i", item) for item in batch])
                payload = response.json()
                data = payload.get("data") if isinstance(payload, dict) else None
                if not isinstance(data, dict):
                    raise ValueError("Kite returned a malformed option quote response.")
                quotes.update(data)
            except (RuntimeError, requests.RequestException, ValueError) as exc:
                failures.append((batch, exc))
        return quotes, failures

    def _spot_price(self, symbol):
        underlying = self._underlying(symbol)
        instrument = self.INDEX_SPOT_SYMBOLS.get(underlying, f"NSE:{underlying}")
        response = self._get("/quote/ltp", params=[("i", instrument)])
        quote = response.json().get("data", {}).get(instrument)
        if not quote:
            raise ValueError(f"Kite returned no spot quote for {instrument}")
        return float(quote["last_price"])

    def available_fno_underlyings(self):
        """Return every currently listed NSE/BSE F&O underlying, indexes included."""
        today = self._today().isoformat()
        return tuple(sorted({
            row.get("name")
            for row in self._load_instruments()
            if row.get("exchange") == "NFO"
            and row.get("instrument_type") in {"CE", "PE"}
            and row.get("expiry", "") >= today
            and row.get("name")
        }))

    def lot_sizes_for_contracts(self, contracts):
        """Find exact contracts in the loaded Kite master without a market request."""
        requested = {}
        for contract in contracts:
            try:
                underlying, expiry, strike, side = contract
                key = (str(underlying).upper(), str(expiry), float(strike), str(side).upper())
            except (TypeError, ValueError):
                continue
            requested[key] = contract
        found = {}
        for row in self._instruments or ():
            if row.get("exchange") not in {"NFO", "BFO"}:
                continue
            try:
                key = (str(row.get("name", "")).upper(), str(row.get("expiry", "")),
                       float(row.get("strike")), str(row.get("instrument_type", "")).upper())
                lot_size = int(row.get("lot_size") or 0)
            except (TypeError, ValueError):
                continue
            if key in requested and lot_size > 0:
                found[requested[key]] = lot_size
        return found

    def _selected_contracts(self, underlying, instruments=None):
        instruments = instruments or self._load_instruments()
        contracts = [
            row
            for row in instruments
            if row.get("exchange") in {"NFO", "BFO"}
            and row.get("instrument_type") in {"CE", "PE"}
            and row.get("name") == underlying
            and row.get("expiry")
        ]
        if not contracts:
            raise ValueError(f"Kite does not list F&O options for {underlying}")

        today = self._today().isoformat()
        expiries = sorted({row["expiry"] for row in contracts if row["expiry"] >= today})
        if not expiries:
            raise ValueError(f"Kite lists no unexpired options for {underlying}")
        # Index instruments can list weekly expiries while stock options are
        # monthly.  The last listed expiry in each calendar month is the
        # monthly contract, which keeps both asset classes on the same curve.
        monthly_expiries = {}
        for expiry in expiries:
            monthly_expiries[expiry[:7]] = expiry
        monthly_values = list(monthly_expiries.values())
        selected_expiries = set(monthly_values[:3])
        if underlying == "NIFTY":
            quarterly = [
                expiry for expiry in monthly_values
                if int(expiry[5:7]) in {3, 6, 9, 12}
            ]
            selected_expiries.update(quarterly[:3])
        return [row for row in contracts if row["expiry"] in selected_expiries]

    @staticmethod
    def _contracts_from_quotes(underlying, rows, quotes):
        result = []
        for row in rows:
            quote_key = f"{row['exchange']}:{row['tradingsymbol']}"
            quote = quotes.get(quote_key)
            if not quote or not quote.get("last_price"):
                continue
            try:
                lot_size = int(row.get("lot_size") or 0)
            except (TypeError, ValueError):
                lot_size = 0
            result.append(
                OptionContract(
                    symbol=underlying,
                    expiry=row["expiry"],
                    strike=float(row["strike"]),
                    option_type=row["instrument_type"],
                    premium=float(quote["last_price"]),
                    volume=int(quote.get("volume") or 0),
                    open_interest=int(quote.get("oi") or 0),
                    implied_volatility=0.0,
                    delta=0.0,
                    theta=0.0,
                    lot_size=lot_size if lot_size > 0 else None,
                )
            )
        return result

    @staticmethod
    def _unusable_quote_keys(quote_keys, quotes):
        """A present key still needs a usable price and market fields."""
        unusable = []
        for key in quote_keys:
            quote = quotes.get(key)
            if not isinstance(quote, dict):
                unusable.append(key)
                continue
            try:
                price = float(quote["last_price"])
                volume = int(quote.get("volume") or 0)
                open_interest = int(quote.get("oi") or 0)
            except (KeyError, TypeError, ValueError, OverflowError):
                unusable.append(key)
                continue
            if not math.isfinite(price) or price <= 0 or volume < 0 or open_interest < 0:
                unusable.append(key)
        return unusable

    def _cached_or_failed(self, underlying, error, chains):
        cached = [
            contract for contract in self._last_chains.get(underlying, ())
            if contract.expiry >= self._today().isoformat()
        ]
        if cached:
            chains[underlying] = cached
            self.stale_symbols.add(underlying)
        else:
            self.stale_symbols.discard(underlying)
            suffix = (
                " No unexpired last-known-good contracts remain."
                if underlying in self._last_chains else ""
            )
            self.chain_failures[underlying] = f"{error}{suffix}"

    def get_option_chains(self, symbols):
        """Fetch three-expiry chains for many underlyings in 400-quote batches.

        A full F&O scan can contain thousands of contracts.  Planning all
        quote keys first avoids one HTTP round trip per underlying while still
        respecting Kite's documented quote-request limit.
        """
        underlyings = tuple(dict.fromkeys(self._underlying(symbol) for symbol in symbols))
        self.chain_failures = {}
        # Status describes this scan, not a symbol left stale in an older
        # universe that the user is no longer requesting.
        self.stale_symbols.intersection_update(underlyings)
        chains = {}

        try:
            instruments = self._load_instruments()
        except (RuntimeError, requests.RequestException) as exc:
            for underlying in underlyings:
                self._cached_or_failed(underlying, exc, chains)
            return chains

        selected_by_underlying = {}
        for underlying in underlyings:
            try:
                selected_by_underlying[underlying] = self._selected_contracts(
                    underlying, instruments
                )
            except ValueError as exc:
                self._cached_or_failed(underlying, exc, chains)

        quote_owners = {
            f"{row['exchange']}:{row['tradingsymbol']}": underlying
            for underlying, rows in selected_by_underlying.items()
            for row in rows
        }
        quote_keys = list(quote_owners)
        quotes, batch_failures = self._quote_resilient(quote_keys)
        failed_underlyings = {}
        for batch, error in batch_failures:
            for quote_key in batch:
                failed_underlyings.setdefault(quote_owners[quote_key], error)

        missing_by_underlying = {}
        for quote_key in set(quote_keys).difference(quotes):
            underlying = quote_owners[quote_key]
            missing_by_underlying.setdefault(underlying, []).append(quote_key)
        for underlying, missing in missing_by_underlying.items():
            failed_underlyings.setdefault(
                underlying,
                ValueError(
                    f"Kite returned an incomplete option chain for {underlying}: "
                    f"{len(missing)} quote(s) missing."
                ),
            )

        for underlying, rows in selected_by_underlying.items():
            keys = [f"{row['exchange']}:{row['tradingsymbol']}" for row in rows]
            unusable = self._unusable_quote_keys(keys, quotes)
            if unusable and underlying not in failed_underlyings:
                failed_underlyings[underlying] = ValueError(
                    f"Kite returned an incomplete option chain for {underlying}: "
                    f"{len(unusable)} quote(s) unusable."
                )

        for underlying, rows in selected_by_underlying.items():
            if underlying in failed_underlyings:
                # Never publish a silently partial chain for an underlying.
                # Its last complete chain is safer; unrelated successful
                # batches can still produce fresh recommendations.
                self._cached_or_failed(
                    underlying, failed_underlyings[underlying], chains
                )
                continue
            contracts = self._contracts_from_quotes(underlying, rows, quotes)
            if not contracts:
                self._cached_or_failed(
                    underlying,
                    ValueError(f"Kite returned no tradable F&O option quotes for {underlying}"),
                    chains,
                )
                continue
            self._last_chains[underlying] = list(contracts)
            self.chain_updated_at[underlying] = self._now().isoformat()
            self.stale_symbols.discard(underlying)
            chains[underlying] = contracts

        return chains

    def get_option_chain(self, symbol):
        underlying = self._underlying(symbol)
        try:
            chain = self._get_option_chain(symbol)
            self.stale_symbols.discard(underlying)
            return chain
        except (RuntimeError, requests.RequestException, ValueError) as exc:
            cached = [
                contract for contract in self._last_chains.get(underlying, ())
                if contract.expiry >= self._today().isoformat()
            ]
            if cached:
                self.stale_symbols.add(underlying)
                return cached
            self.stale_symbols.discard(underlying)
            if underlying in self._last_chains:
                raise RuntimeError(
                    f"{exc} No unexpired last-known-good contracts remain."
                ) from exc
            raise

    def _get_option_chain(self, symbol):
        underlying = self._underlying(symbol)
        selected = self._selected_contracts(underlying)
        quote_keys = [f"{row['exchange']}:{row['tradingsymbol']}" for row in selected]
        quotes = self._quote(quote_keys)
        missing = set(quote_keys).difference(quotes)
        if missing:
            raise ValueError(
                f"Kite returned an incomplete option chain for {underlying}: "
                f"{len(missing)} quote(s) missing."
            )
        unusable = self._unusable_quote_keys(quote_keys, quotes)
        if unusable:
            raise ValueError(
                f"Kite returned an incomplete option chain for {underlying}: "
                f"{len(unusable)} quote(s) unusable."
            )
        result = self._contracts_from_quotes(underlying, selected, quotes)
        if not result:
            raise ValueError(f"Kite returned no tradable F&O option quotes for {underlying}")
        self._last_chains[underlying] = list(result)
        self.chain_updated_at[underlying] = self._now().isoformat()
        return result
