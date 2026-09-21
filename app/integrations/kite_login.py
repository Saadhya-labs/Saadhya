"""Local, read-only Kite Connect login helper.

The request token is received only on the configured loopback callback and is
exchanged locally. Neither credentials nor tokens are sent to Saadhya.
"""

from __future__ import annotations

import hashlib
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import set_key


class KiteLoginError(ValueError):
    pass


def local_config_path():
    """Find the local configuration beside the executable or source checkout."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / ".env"
    return Path.cwd() / ".env"


class KiteLogin:
    TOKEN_URL = "https://api.kite.trade/session/token"

    def __init__(self, api_key, api_secret, redirect_url, session=None):
        if not api_key or not api_secret:
            raise KiteLoginError(
                "Add KITE_API_KEY and KITE_API_SECRET to the local .env file first."
            )
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_url = redirect_url
        self.session = session or requests.Session()
        self._callback = urlparse(redirect_url)
        if self._callback.scheme != "http" or self._callback.hostname not in {
            "127.0.0.1", "localhost",
        }:
            raise KiteLoginError(
                "Kite desktop login requires a local callback such as "
                "http://127.0.0.1:8000/kite/callback."
            )

    @property
    def login_url(self):
        return f"https://kite.zerodha.com/connect/login?v=3&api_key={self.api_key}"

    def authenticate(self, timeout=300, open_browser=True):
        """Open Kite login, receive one request token, and persist the session token."""
        request_token = self._receive_request_token(timeout, open_browser)
        checksum = hashlib.sha256(
            f"{self.api_key}{request_token}{self.api_secret}".encode("utf-8")
        ).hexdigest()
        response = self.session.post(
            self.TOKEN_URL,
            headers={"X-Kite-Version": "3"},
            data={
                "api_key": self.api_key,
                "request_token": request_token,
                "checksum": checksum,
            },
            timeout=20,
        )
        response.raise_for_status()
        access_token = response.json().get("data", {}).get("access_token")
        if not access_token:
            raise KiteLoginError("Kite login completed but did not return an access token.")
        set_key(str(local_config_path()), "KITE_ACCESS_TOKEN", access_token)
        os.environ["KITE_ACCESS_TOKEN"] = access_token
        return access_token

    def _receive_request_token(self, timeout, open_browser):
        callback_path = self._callback.path or "/"
        received = {}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802 - required by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path != callback_path:
                    self.send_error(404)
                    return
                query = parse_qs(parsed.query)
                received["request_token"] = query.get("request_token", [None])[0]
                received["status"] = query.get("status", [None])[0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"<h2>Saadhya is connected to Kite.</h2>"
                    b"<p>You can close this tab and return to Saadhya.</p>"
                )

            def log_message(self, _format, *_args):
                return

        server = HTTPServer((self._callback.hostname, self._callback.port or 80), CallbackHandler)
        server.timeout = timeout
        try:
            if open_browser:
                if not webbrowser.open(self.login_url):
                    raise KiteLoginError("The Kite login page could not be opened in the browser.")
            server.handle_request()
        finally:
            server.server_close()
        if received.get("status") != "success" or not received.get("request_token"):
            raise KiteLoginError(
                "Kite sign-in was cancelled, timed out, or did not return a request token."
            )
        return received["request_token"]
