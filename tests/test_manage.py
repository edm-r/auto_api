import sys

import pytest

import manage


def test_main_success(mocker, monkeypatch):
    execute_mock = mocker.patch("django.core.management.execute_from_command_line")
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(sys, "argv", ["manage.py", "check"])

    manage.main()

    assert sys.argv == ["manage.py", "check"]
    execute_mock.assert_called_once_with(["manage.py", "check"])


def test_main_raises_exception(mocker):
    import builtins

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "django.core.management":
            raise ImportError("forced import error")
        return original_import(name, *args, **kwargs)

    mocker.patch("builtins.__import__", side_effect=fake_import)

    with pytest.raises(ImportError) as exc_info:
        manage.main()

    assert "Couldn't import Django." in str(exc_info.value)
