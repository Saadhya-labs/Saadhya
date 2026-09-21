from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_recommendation_app_has_no_kite_token_exchange_or_persistence():
    recommendation_paths = (
        PROJECT_ROOT / "app" / "gui" / "desktop.py",
        PROJECT_ROOT / "app" / "cli" / "market_scan.py",
        PROJECT_ROOT / "app" / "config" / "provider_factory.py",
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in recommendation_paths)

    assert not (PROJECT_ROOT / "app" / "integrations" / "kite_login.py").exists()
    assert "KiteLogin" not in source
    assert "request_token" not in source
    assert "session/token" not in source
    assert "KITE_API_SECRET" not in source
    assert "persist_access_token" not in source
