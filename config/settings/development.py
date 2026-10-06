from .base import *  # noqa: F401, F403

DEBUG = True

if not SECRET_KEY:
    SECRET_KEY = "django-insecure-dev-key-do-not-use-in-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
X_FRAME_OPTIONS = "SAMEORIGIN"
CORS_ALLOW_ALL_ORIGINS = True

# Local convenience only: seed admin/admin123 on migrate in development.
SEED_DEFAULT_ADMIN = True
DEFAULT_ADMIN_PASSWORD = "admin123"
