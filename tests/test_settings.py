from app.config.settings import Settings


def test_settings_defaults():

    assert Settings.APP_ENV == "development"

    assert Settings.BROKER == "paper"

    assert Settings.STARTING_CAPITAL == 1000000

    assert Settings.DEFAULT_SYMBOL == "HAL.NS"