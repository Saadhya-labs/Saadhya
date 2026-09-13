"""Interactive Kite authentication for read-only market-data access."""

from __future__ import annotations

import hashlib
import os
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import requests


class KiteLogin:
    LOGIN_URL = "https://kite.zerodha.com/connect/login"
    SESSION_URL = "https://api.kite.trade/session/token"

    def __init__(self, api_key, api_secret, redirect_url, session=None, timeout=180):
        if not api_key or not api_secret:
            raise ValueError("Set KITE_API_KEY and KITE_API_SECRET in Saadhya's .env file first.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_url = redirect_url
        self.session = session or requests.Session()
        self.timeout = timeout

    def authenticate(self):
        callback = urlparse(self.redirect_url)
        if callback.scheme != "http" or callback.hostname not in {"127.0.0.1", "localhost"}:
            raise ValueError("KITE_REDIRECT_URL must be a local http://127.0.0.1 callback URL.")
        request_token = self._receive_request_token(callback)
        checksum = hashlib.sha256(
            f"{self.api_key}{request_token}{self.api_secret}".encode("utf-8")
        ).hexdigest()
        response = self.session.post(
            self.SESSION_URL,
            data={"api_key": self.api_key, "request_token": request_token, "checksum": checksum},
            headers={"X-Kite-Version": "3"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        access_token = payload.get("data", {}).get("access_token")
        if not access_token:
            raise RuntimeError("Kite did not return an access token.")
        os.environ["KITE_ACCESS_TOKEN"] = access_token
        self._persist_access_token(access_token)
        return access_token

    def _receive_request_token(self, callback):
        result = {}
        expected_path = callback.path or "/"

        class Handler(BaseHTTPRequestHandler):
            def do_GET(handler):
                parsed = urlparse(handler.path)
                values = parse_qs(parsed.query)
                if parsed.path == expected_path and values.get("request_token"):
                    result["request_token"] = values["request_token"][0]
                    message = b"Kite connected to Saadhya. You can close this browser tab."
                    handler.send_response(200)
                else:
                    result["error"] = values.get("message", ["Kite login was not completed."])[0]
                    message = b"Kite connection failed. Return to Saadhya and try again."
                    handler.send_response(400)
                handler.send_header("Content-Type", "text/plain; charset=utf-8")
                handler.send_header("Content-Length", str(len(message)))
                handler.end_headers()
                handler.wfile.write(message)

            def log_message(self, _format, *_args):
                return

        port = callback.port or 80
        server = HTTPServer((callback.hostname, port), Handler)
        server.timeout = 1
        login_url = f"{self.LOGIN_URL}?{urlencode({'v': 3, 'api_key': self.api_key})}"
        webbrowser.open(login_url)
        deadline = time.monotonic() + self.timeout
        try:
            while not result and time.monotonic() < deadline:
                server.handle_request()
        finally:
            server.server_close()
        if "request_token" not in result:
            raise RuntimeError(result.get("error", "Kite sign-in timed out. Please try again."))
        return result["request_token"]

    @staticmethod
    def _environment_path():
        candidates = [Path.cwd() / ".env"]
        if getattr(sys, "frozen", False):
            executable_dir = Path(sys.executable).resolve().parent
            candidates.extend((executable_dir / ".env", executable_dir.parent / ".env"))
        return next((path for path in candidates if path.is_file()), candidates[-1])

    def _persist_access_token(self, token):
        path = self._environment_path()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            lines = []
        replacement = f"KITE_ACCESS_TOKEN={token}"
        updated = []
        found = False
        for line in lines:
            if line.startswith("KITE_ACCESS_TOKEN="):
                updated.append(replacement)
                found = True
            else:
                updated.append(line)
        if not found:
            updated.append(replacement)
        path.write_text("\n".join(updated) + "\n", encoding="utf-8")
