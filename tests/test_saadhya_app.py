from app.core.saadhya_app import SaadhyaApp


def test_saadhya_app_initializes():

    app = SaadhyaApp()

    assert app.analyzer is not None

    assert not hasattr(app, "place_trade")



def test_saadhya_app_uses_default_symbol():

    app = SaadhyaApp()

    assert app.settings.DEFAULT_SYMBOL == "HAL.NS"

    assert app.settings.RECOMMENDATION_ONLY is True
