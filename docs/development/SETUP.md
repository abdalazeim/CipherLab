# Setup & Development

## 1. Requirements

- Python 3.11+
- Django 5.2+ (see `requirements.txt`)
- PostgreSQL 16+ for production (optional locally; SQLite is the default)

## 2. Installation

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
copy .env.example .env         # Windows
cp .env.example .env           # Linux / macOS
```

The default `.env` runs on SQLite (`db.sqlite3`) with `DEBUG=True` — no database
configuration is required to start developing.

## 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

Optional: seed runtime settings (core + example data only, no business data):

```bash
python manage.py seed_data
```

Create a superuser:

```bash
python manage.py createsuperuser
# or, if DJANGO_SEED_ADMIN=true is set in .env, an admin is auto-created on migrate
```

## 4. Run the Development Server

```bash
python manage.py runserver
# or the convenience wrapper
python scripts/run.py
```

- Default settings: `config.settings.development`
- Server: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin/
- Health checks: http://127.0.0.1:8000/health/ and /health/db/

## 5. Environment Variables

All variables are read in `config/settings/base.py` via `django-environ`. Copy
`.env.example` to `.env` and adjust.

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `False` | Django debug mode |
| `SECRET_KEY` | — | Django secret key (required in production) |
| `DATABASE_URL` | — | PostgreSQL connection string (unset = SQLite) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | — | Comma-separated trusted origins (prod) |
| `CORS_ALLOWED_ORIGINS` | — | Comma-separated allowed CORS origins |
| `SESSION_COOKIE_SECURE` | `False` | Set True behind HTTPS |
| `CSRF_COOKIE_SECURE` | `False` | Set True behind HTTPS |
| `SECURE_SSL_REDIRECT` | `False` | Redirect HTTP→HTTPS |
| `SECURE_HSTS_SECONDS` | `0` | HSTS duration |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` / `DEFAULT_FROM_EMAIL` | — | SMTP; falls back to console backend |
| `RATE_LIMIT_LOGIN` | `10/m` | Login endpoint rate limit |
| `RATE_LIMIT_API` | `60/m` | API rate limit |
| `DJANGO_SEED_ADMIN` | `False` | Auto-create admin on migrate |
| `DJANGO_ADMIN_USERNAME` / `DJANGO_ADMIN_EMAIL` / `DJANGO_ADMIN_PASSWORD` | — | Admin credentials when seeding |
| `LANGUAGE_CODE` | `ar` | Default language (ar/en) |
| `APP_FONT_FAMILY` | `Cairo` | UI font family (Cairo/Tajawal) |
| `TZ` | `Asia/Riyadh` | Time zone |
| `SITE_TITLE` | `نظام إدارة عام` | UI site title |
| `SITE_SUBTITLE` | `General Development System` | UI site subtitle |

> Never commit `.env` to Git. Only `.env.example` is versioned.

## 6. Daily Commands

```bash
python manage.py check                      # system check
python manage.py makemigrations --check     # detect missing migrations
python manage.py test                       # run all tests
python manage.py seed_data                  # seed runtime settings
python manage.py backup_db                  # backup database
python manage.py health_check               # system health (if installed)
python scripts/verify_api.py                # smoke-test all API endpoints
python scripts/check_static_refs.py         # verify {% static %} references
```

## 7. Language & Fonts

- Two languages are supported out of the box: `ar` (RTL, default) and `en` (LTR).
- Switch language at runtime via `?lang=en` / `?lang=ar` (handled by
  `LanguageSwitchMiddleware`, which persists the choice to the session and cookie).
- Arabic fonts (Tajawal 400/500/700) are bundled locally under
  `static/vendor/tajawal/`; the active font family comes from the `ui_font_family`
  system setting or `APP_FONT_FAMILY`.
- UI text strings use `{% trans %}` / `gettext` where translatable; compiled
  catalogs go under `locale/`.
