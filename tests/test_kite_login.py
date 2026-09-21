import hashlib


def test_kite_login_exchanges_request_token_and_persists_access_token(monkeypatch, tmp_path):
    from app.integrations import kite_login

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": {"access_token": "daily-token"}}

    class Session:
        def post(self, url, headers, data, timeout):
            self.call = (url, headers, data, timeout)
            return Response()

    session = Session()
    login = kite_login.KiteLogin(
        "api-key", "api-secret", "http://127.0.0.1:8000/kite/callback", session=session,
    )
    monkeypatch.setattr(login, "_receive_request_token", lambda timeout, open_browser: "request-token")
    monkeypatch.setattr(kite_login, "local_config_path", lambda: tmp_path / ".env")

    assert login.authenticate(open_browser=False) == "daily-token"
    expected = hashlib.sha256(b"api-keyrequest-tokenapi-secret").hexdigest()
    assert session.call[2]["checksum"] == expected
    assert "KITE_ACCESS_TOKEN='daily-token'" in (tmp_path / ".env").read_text(encoding="utf-8")
