"""Validated configuration for Saadhya's recommendation-only runtime."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _load_local_environment():
    """Load a local config beside the project or packaged executable.

    The Windows bundle lives in ``outputs`` while the user-managed ``.env``
    normally remains in the project folder.  Search both locations without
    overriding environment values supplied by the operating system.
    """
    candidates = [Path.cwd() / ".env"]
    if getattr(sys, "frozen", False):
        executable_directory = Path(sys.executable).resolve().parent
        candidates.extend((executable_directory / ".env", executable_directory.parent / ".env"))
    for candidate in candidates:
        if candidate.is_file():
            load_dotenv(candidate, override=False)


_load_local_environment()


@dataclass(frozen=True)
class RuntimeSettings:
    app_env: str
    data_mode: str
    default_symbol: str
    scan_symbols: tuple[str, ...]
    scan_limit: int


def _symbols(value: str) -> tuple[str, ...]:
    symbols = tuple(symbol.strip().upper() for symbol in value.split(",") if symbol.strip())
    if not symbols:
        raise ValueError("SCAN_SYMBOLS must contain at least one symbol")
    return symbols


def load_settings(environ=None) -> RuntimeSettings:
    environ = os.environ if environ is None else environ
    data_mode = environ.get("DATA_MODE", "kite").strip().lower()
    if data_mode not in {"mock", "live", "kite"}:
        raise ValueError("DATA_MODE must be 'mock', 'live', or 'kite'")

    default_symbol = environ.get("DEFAULT_SYMBOL", "HAL.NS").strip().upper()
    if not default_symbol:
        raise ValueError("DEFAULT_SYMBOL must not be empty")

    try:
        scan_limit = int(environ.get("SCAN_LIMIT", "10"))
    except ValueError as exc:
        raise ValueError("SCAN_LIMIT must be an integer") from exc
    if scan_limit < 1:
        raise ValueError("SCAN_LIMIT must be greater than zero")

    return RuntimeSettings(
        app_env=environ.get("APP_ENV", "development").strip().lower(),
        data_mode=data_mode,
        default_symbol=default_symbol,
        scan_symbols=_symbols(environ.get("SCAN_SYMBOLS", default_symbol)),
        scan_limit=scan_limit,
    )


_runtime = load_settings()


class Settings:
    """Compatibility facade for application configuration."""

    APP_ENV = _runtime.app_env
    DATA_MODE = _runtime.data_mode
    DEFAULT_SYMBOL = _runtime.default_symbol
    SCAN_SYMBOLS = _runtime.scan_symbols
    SCAN_LIMIT = _runtime.scan_limit
    RECOMMENDATION_ONLY = True


DATA_MODE = Settings.DATA_MODE
