import os


class Secrets:

    ZERODHA_API_KEY = os.getenv(
        "ZERODHA_API_KEY"
    )

    ZERODHA_API_SECRET = os.getenv(
        "ZERODHA_API_SECRET"
    )

    ZERODHA_ACCESS_TOKEN = os.getenv(
        "ZERODHA_ACCESS_TOKEN"
    )