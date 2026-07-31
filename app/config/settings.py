import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    APP_ENV = os.getenv(
        "APP_ENV",
        "development"
    )


    BROKER = os.getenv(
        "BROKER",
        "paper"
    )


    STARTING_CAPITAL = int(
        os.getenv(
            "STARTING_CAPITAL",
            1000000
        )
    )


    DEFAULT_SYMBOL = os.getenv(
        "DEFAULT_SYMBOL",
        "HAL.NS"
    )


    DATA_MODE = os.getenv(
        "DATA_MODE",
        "mock"
    )


DATA_MODE = Settings.DATA_MODE