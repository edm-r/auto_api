import importlib


def test_asgi_application_success():
    module = importlib.import_module("auto_api.asgi")
    reloaded_module = importlib.reload(module)

    assert reloaded_module.application is not None


def test_wsgi_application_success():
    module = importlib.import_module("auto_api.wsgi")
    reloaded_module = importlib.reload(module)

    assert reloaded_module.application is not None


def test_settings_render_external_hostname_edge_case(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("ALLOWED_HOSTS", "")
    monkeypatch.setenv("RENDER_EXTERNAL_HOSTNAME", "example.onrender.com")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

    module = importlib.import_module("auto_api.settings")
    reloaded_module = importlib.reload(module)

    assert "example.onrender.com" in reloaded_module.ALLOWED_HOSTS
    assert "https://example.onrender.com" in reloaded_module.CSRF_TRUSTED_ORIGINS


def test_settings_database_url_success(monkeypatch):
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tmp/settings-test.sqlite3")
    monkeypatch.delenv("DB_NAME", raising=False)

    module = importlib.import_module("auto_api.settings")
    reloaded_module = importlib.reload(module)

    assert reloaded_module.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"


def test_settings_db_name_edge_case(monkeypatch):
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_NAME", "auto_api_db")
    monkeypatch.setenv("DB_USER", "api_user")
    monkeypatch.setenv("DB_PASSWORD", "api_password")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")

    module = importlib.import_module("auto_api.settings")
    reloaded_module = importlib.reload(module)

    assert reloaded_module.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert reloaded_module.DATABASES["default"]["NAME"] == "auto_api_db"
