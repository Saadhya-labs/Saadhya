from app.core.saadhya_app import SaadhyaApp


def test_saadhya_app_initializes():

    app = SaadhyaApp()

    assert app.broker is not None

    assert app.analyzer is not None



def test_saadhya_app_uses_default_symbol():

    app = SaadhyaApp()

    assert app.settings.DEFAULT_SYMBOL == "HAL.NS"