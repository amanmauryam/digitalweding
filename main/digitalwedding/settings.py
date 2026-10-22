"""Django settings for the DigitalWedding project.

Target stack (per design.md): Python 3.12+, Django 5.x, PostgreSQL,
Tailwind CSS, Alpine.js / HTMX.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
if DEBUG:
    ALLOWED_HOSTS.append("*")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "invitations",
    "websites",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "digitalwedding.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "invitations.context_processors.site_context",
                "invitations.context_processors.language_context",
            ],
        },
    },
]

WSGI_APPLICATION = "digitalwedding.wsgi.application"
ASGI_APPLICATION = "digitalwedding.asgi.application"

# --------------------------------------------------------------------------
# Database: PostgreSQL in production, SQLite for zero-config local dev.
# --------------------------------------------------------------------------
DB_ENGINE = os.environ.get("DB_ENGINE", "django.db.backends.postgresql")
DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    from urllib.parse import unquote, urlparse

    parsed = urlparse(DATABASE_URL)
    if parsed.scheme.startswith("postgres"):
        DB_ENGINE = "django.db.backends.postgresql"
        DB_NAME = unquote(parsed.path.lstrip("/"))
        DB_USER = unquote(parsed.username or "postgres")
        DB_PASSWORD = unquote(parsed.password or "")
        DB_HOST = parsed.hostname or "localhost"
        DB_PORT = str(parsed.port or 5432)
    else:
        raise ValueError(
            f"Unsupported DATABASE_URL scheme: {parsed.scheme!r} (use postgres://…)"
        )

if DB_NAME and DB_ENGINE.endswith("postgresql"):
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "hi"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("hi", "Hindi"),
    ("mai", "Maithili"),
    ("bho", "Bhojpuri"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Private storage: original invitation cards never live inside MEDIA_ROOT, so
# they can never be served by Django's development media server.
PRIVATE_UPLOAD_ROOT = BASE_DIR / "private_uploads"

# --------------------------------------------------------------------------
# Wedding website builder limits (all configurable through the environment)
# --------------------------------------------------------------------------
WEDDING_INVITATION_MAX_MB = int(os.environ.get("WEDDING_INVITATION_MAX_MB", "10"))
WEDDING_INVITATION_MAX_PAGES = int(
    os.environ.get("WEDDING_INVITATION_MAX_PAGES", "20")
)
WEDDING_INVITATION_ALLOWED_EXTENSIONS = tuple(
    item.strip().lower()
    for item in os.environ.get(
        "WEDDING_INVITATION_ALLOWED_EXTENSIONS", "jpg,jpeg,png,webp,pdf"
    ).split(",")
    if item.strip()
)
WEDDING_INVITATION_MIN_TEXT_CHARS = int(
    os.environ.get("WEDDING_INVITATION_MIN_TEXT_CHARS", "40")
)
WEDDING_PHOTO_MAX_MB = int(os.environ.get("WEDDING_PHOTO_MAX_MB", "8"))
WEDDING_RSVP_MIN_SECONDS = int(os.environ.get("WEDDING_RSVP_MIN_SECONDS", "3"))
WEDDING_RSVP_RATE_LIMIT = int(os.environ.get("WEDDING_RSVP_RATE_LIMIT", "8"))
WEDDING_RSVP_RATE_WINDOW = int(os.environ.get("WEDDING_RSVP_RATE_WINDOW", "3600"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "invitations:dashboard"
LOGOUT_REDIRECT_URL = "invitations:home"

# --------------------------------------------------------------------------
# DigitalWedding business settings
# --------------------------------------------------------------------------
SUPPORT_WHATSAPP = os.environ.get(
    "DW_SUPPORT_WHATSAPP", os.environ.get("SUPPORT_WHATSAPP", "+910000000000")
)
SUPPORT_EMAIL = os.environ.get(
    "DW_SUPPORT_EMAIL", os.environ.get("SUPPORT_EMAIL", "hello@digitalwedding.in")
)
DEFAULT_SITE_URL = os.environ.get("DEFAULT_SITE_URL", "http://127.0.0.1:8000")

# Folk music is opt-in and paused until the guest taps the screen.
AUDIO_DEFAULT_PAUSED = True

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_SAVE_EVERY_REQUEST = False

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

if not DEBUG:
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
