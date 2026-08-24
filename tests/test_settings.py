import pytest

from app.config.settings import Settings, load_settings


def test_settings_defaults():

    assert Settings.APP_ENV == "development"

    assert Settings.DEFAULT_SYMBOL == "HAL.NS"

    assert Settings.RECOMMENDATION_ONLY is True


def test_settings_validate_data_mode_and_scan_limit():
    with pytest.raises(ValueError, match="DATA_MODE"):
        load_settings({"DATA_MODE": "broker"})

    with pytest.raises(ValueError, match="SCAN_LIMIT"):
        load_settings({"SCAN_LIMIT": "zero"})
