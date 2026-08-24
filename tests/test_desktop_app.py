def test_desktop_application_module_is_importable():
    from app.gui.desktop import SaadhyaDesktopApp

    assert SaadhyaDesktopApp.__name__ == "SaadhyaDesktopApp"
