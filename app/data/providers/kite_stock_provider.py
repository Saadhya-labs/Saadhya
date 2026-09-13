"""Read-only Kite Connect market-data provider.

This module deliberately uses only Kite's instrument, quote, and historical
market-data endpoints.  It contains no order, portfolio, or execution calls.
"""

from __future__ import annotations

import csv
import json
import re
import time
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from app.data.providers.stock_provider import StockDataProvider


class KiteConfigurationError(ValueError):
    """Raised when the local read-only Kite configuration is incomplete."""


class KiteStockProvider(StockDataProvider):
    API_ROOT = "https://api.kite.trade"

    QUOTE_BATCH_SIZE = 400
    # Daily technical candles do not need to be downloaded for every refresh.
    # Live prices and option premiums are fetched separately on every scan.
    HISTORY_CACHE_SECONDS = 6 * 60 * 60
    INDEX_TRADING_SYMBOLS = {
        "NIFTY": "NIFTY 50",
        "BANKNIFTY": "NIFTY BANK",
        "FINNIFTY": "NIFTY FIN SERVICE",
        "MIDCPNIFTY": "NIFTY MID SELECT",
    }

    def __init__(
        self, api_key=None, access_token=None, session=None, now=None, retries=3,
        history_cache_dir=None,
    ):
        self.api_key = api_key
        self.access_token = access_token
        self.session = session or requests.Session()
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._instruments = None
        self._instruments_date = None
        self.instrument_master_stale = False
        self.instrument_master_error = None
        self.retries = max(1, retries)
        self._last_prices = {}
        self._last_history = {}
        self._history_fetched_at = {}
        self.history_cache_dir = Path(
            history_cache_dir or (Path.home() / ".saadhya" / "cache" / "kite-history")
        )
        self.stale_symbols = set()
        if not self.api_key or not self.access_token:
            raise KiteConfigurationError(
                "Kite mode requires KITE_API_KEY and a current KITE_ACCESS_TOKEN. "
                "Configure the read-only market-data session outside Saadhya."
            )

    @property
    def headers(self):
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}",
        }

    @staticmethod
    def _trading_symbol(symbol):
        return symbol.upper().replace(".NS", "").replace("NSE:", "")

    def _get(self, path, **kwargs):
        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(
                    f"{self.API_ROOT}{path}", headers=self.headers, timeout=15, **kwargs
                )
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(0.25 * (2**attempt))
        raise RuntimeError(f"Kite market data is temporarily unavailable: {last_error}") from last_error

    def _load_instruments(self):
        current_date = self._now().date()
        if self._instruments is None or self._instruments_date != current_date:
            try:
                content = self._get("/instruments/NSE").text
                instruments = list(csv.DictReader(StringIO(content)))
                if not any(
                    row.get("instrument_token")
                    and row.get("tradingsymbol")
                    and (
                        row.get("instrument_type") == "EQ"
                        or row.get("segment") == "INDICES"
                    )
                    for row in instruments
                ):
                    raise ValueError("Kite returned an empty or malformed NSE instrument master.")
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

    def _instrument_token(self, symbol):
        trading_symbol = self.INDEX_TRADING_SYMBOLS.get(
            self._trading_symbol(symbol), self._trading_symbol(symbol)
        )
        for instrument in self._load_instruments():
            if instrument["tradingsymbol"] == trading_symbol and (
                instrument.get("instrument_type") == "EQ"
                or instrument.get("segment") == "INDICES"
            ):
                return instrument["instrument_token"]
        raise ValueError(f"Kite does not list NSE equity instrument {trading_symbol}")

    def available_nse_equities(self):
        """Return the current Kite NSE equity universe for broad scans."""
        return tuple(
            f"{row['tradingsymbol']}.NS"
            for row in self._load_instruments()
            if row.get("instrument_type") == "EQ" and row.get("tradingsymbol")
        )

    def _period_start(self, period):
        periods = {
            "5d": timedelta(days=7),
            "1mo": timedelta(days=31),
            "3mo": timedelta(days=93),
            "6mo": timedelta(days=186),
            "1y": timedelta(days=366),
        }
        return self._now() - periods.get(period, periods["6mo"])

    def _history_cache_path(self, cache_key):
        symbol, period = cache_key
        safe_symbol = re.sub(r"[^A-Z0-9_.-]", "_", symbol)
        return self.history_cache_dir / f"{safe_symbol}-{period}.json"

    def _history_is_fresh(self, fetched_at):
        age_seconds = (self._now() - fetched_at).total_seconds()
        # A cache timestamp in the future usually means the system clock moved
        # backwards. Treat it as invalid instead of reusing it indefinitely.
        return 0 <= age_seconds < self.HISTORY_CACHE_SECONDS

    def _load_persistent_history(self, cache_key):
        path = self._history_cache_path(cache_key)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(payload["fetched_at"])
            if not self._history_is_fresh(fetched_at):
                return None
            frame = pd.read_json(
                StringIO(payload["frame"]), orient="split", convert_dates=False
            )
        except (FileNotFoundError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None
        self._last_history[cache_key] = frame
        self._history_fetched_at[cache_key] = fetched_at
        return frame.copy()

    def _save_persistent_history(self, cache_key, frame, fetched_at):
        try:
            self.history_cache_dir.mkdir(parents=True, exist_ok=True)
            path = self._history_cache_path(cache_key)
            temporary = path.with_suffix(".tmp")
            temporary.write_text(
                json.dumps({
                    "fetched_at": fetched_at.isoformat(),
                    "frame": frame.to_json(orient="split", date_format="iso"),
                }),
                encoding="utf-8",
            )
            temporary.replace(path)
        except OSError:
            # A read-only installation may still use the in-memory cache.
            pass

    def get_history(self, symbol, period="6mo"):
        cache_key = (symbol.upper(), period)
        fetched_at = self._history_fetched_at.get(cache_key)
        if (
            cache_key in self._last_history
            and fetched_at is not None
            and self._history_is_fresh(fetched_at)
        ):
            return self._last_history[cache_key].copy()
        persistent = self._load_persistent_history(cache_key)
        if persistent is not None:
            return persistent
        try:
            token = self._instrument_token(symbol)
            start = self._period_start(period)
            end = self._now()
            response = self._get(
                f"/instruments/historical/{token}/day",
                params={
                    "from": start.strftime("%Y-%m-%d %H:%M:%S"),
                    "to": end.strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            candles = response.json().get("data", {}).get("candles", [])
            if not candles:
                raise ValueError(f"Kite returned no historical candles for {symbol}")
            frame = pd.DataFrame(
                candles,
                columns=["Date", "Open", "High", "Low", "Close", "Volume"],
            ).set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]
            fetched_at = self._now()
            self._last_history[cache_key] = frame.copy()
            self._history_fetched_at[cache_key] = fetched_at
            self._save_persistent_history(cache_key, frame, fetched_at)
            self.stale_symbols.discard(symbol.upper())
            return frame
        except (RuntimeError, ValueError):
            if cache_key in self._last_history:
                self.stale_symbols.add(symbol.upper())
                return self._last_history[cache_key].copy()
            raise

    def get_price(self, symbol):
        trading_symbol = self._trading_symbol(symbol)
        trading_symbol = self.INDEX_TRADING_SYMBOLS.get(trading_symbol, trading_symbol)
        instrument = f"NSE:{trading_symbol}"
        try:
            response = self._get("/quote/ltp", params=[("i", instrument)])
            data = response.json().get("data", {})
            if instrument not in data:
                raise ValueError(f"Kite returned no live quote for {instrument}")
            price = float(data[instrument]["last_price"])
            self._last_prices[instrument] = price
            self.stale_symbols.discard(symbol.upper())
            return price
        except (RuntimeError, ValueError):
            if instrument in self._last_prices:
                self.stale_symbols.add(symbol.upper())
                return self._last_prices[instrument]
            raise
