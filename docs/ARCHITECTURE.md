# GDS-Template — Architecture (Top-Level)

This is the **Reusable Django Enterprise Starter Template** ("General Development
System"). It is a domain-independent core that any business project can start
from by adding business modules under `apps/modules/`.

See the detailed guides:

| Topic | Document |
|-------|----------|
| Architecture & layering | `docs/architecture/ARCHITECTURE.md` |
| Creating a business module | `docs/architecture/MODULES.md` |
| Setup & environment | `docs/development/SETUP.md` |
| Testing | `docs/development/TESTING.md` |
| Database & migrations | `docs/database/DATABASE.md` |
| API (versioning, envelope, auth) | `docs/api/API.md` |
| Security & logging | `docs/security/SECURITY.md` |
| Deployment (Docker/Render/Nginx) | `docs/deployment/DEPLOYMENT.md` |

## Quick Layout

```
manage.py                 # auto-selects settings (development / production)
config/                   # settings (base/dev/test/prod/desktop) + urls + api_urls
apps/
├── core/                 # domain-independent: BaseModel, AuditLog, SystemSettings,
│                         #   utils, middleware, validators, services, API helpers
├── accounts/             # custom User, auth, roles, permissions, audit
└── modules/
    ├── example/          # reference module (copy to start a new module)
    ├── warehouse/        # legacy reference (working example)
    ├── purchasing/       # legacy reference (working example)
    └── inventory/        # legacy reference (working example)
templates/                # base/layouts/pages/components/partials
static/                   # css/js/fonts/images/vendor
tests/                    # unit/integration/e2e
scripts/                  # verify_api, check_static_refs, run, deploy
deployment/               # docker, nginx, gunicorn, systemd
docs/                     # this documentation tree
```

## Dependency Rule

```
Core  ←  Accounts  ←  Business Modules
```

Core never imports business modules. Modules can be added or removed without
touching Core.

## Settings Modules

| Module | Use |
|--------|-----|
| `config.settings.development` | default for `manage.py` / `runserver` |
| `config.settings.test` | fast SQLite test database |
| `config.settings.production` | secure, used by Render (`PORT`/`RENDER` set) |
| `config.settings.desktop` | PyInstaller offline desktop mode |

## API

- Mounted at `/api/` (default) and `/api/v1/` (versioned); future `v2` added
  without breaking v1.
- Unified envelope: `{ success, message, data, errors }`.
- Session-based auth; `api_login_required` / `api_permission_required`.
- Health: `/health/` and `/health/db/`.

## Verification

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
python scripts/verify_api.py
python scripts/check_static_refs.py
```
