from app.config.secrets import Secrets


def test_secrets_exist():

    assert hasattr(
        Secrets,
        "ZERODHA_API_KEY"
    )

    assert hasattr(
        Secrets,
        "ZERODHA_API_SECRET"
    )