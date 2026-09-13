import hashlib
import os

from app.integrations.kite_login import KiteLogin


class Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {"data": {"access_token": "daily-token"}}


class Session:
    def __init__(self):
        self.request = None

    def post(self, url, **kwargs):
        self.request = (url, kwargs)
        return Response()


def test_kite_login_exchanges_and_persists_daily_token(tmp_path, monkeypatch):
    session = Session()
    login = KiteLogin("key", "secret", "http://127.0.0.1:8000/kite/callback", session=session)
    monkeypatch.setattr(login, "_receive_request_token", lambda callback: "request-token")
    monkeypatch.setattr(login, "_environment_path", lambda: tmp_path / ".env")

    assert login.authenticate() == "daily-token"

    expected = hashlib.sha256(b"keyrequest-tokensecret").hexdigest()
    assert session.request[1]["data"]["checksum"] == expected
    assert (tmp_path / ".env").read_text(encoding="utf-8") == "KITE_ACCESS_TOKEN=daily-token\n"
    assert os.environ["KITE_ACCESS_TOKEN"] == "daily-token"
