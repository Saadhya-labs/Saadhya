def test_desktop_application_module_is_importable():
    from app.gui.desktop import SaadhyaDesktopApp
    from app.scanner.universe import NSE_STOCKS

    assert SaadhyaDesktopApp.__name__ == "SaadhyaDesktopApp"
    assert len(NSE_STOCKS) > 1
