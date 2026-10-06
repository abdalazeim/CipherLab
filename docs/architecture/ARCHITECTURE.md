# Architecture

> General Development System (GDS) — Reusable Django Enterprise Starter Template

## 1. Design Principle

The template is split into **Core + Accounts + Reusable Services + Optional Business
Modules**. The Core is fully independent of any business domain; business modules can
be added or removed without touching it.

```
CORE
 └── Authentication, Authorization, Users, Roles, Permissions, Settings,
     Audit Log, Notifications, Attachments, Common Utilities,
     API Infrastructure, Error Handling, System Configuration
```

Business modules live under `apps/modules/` and are optional:

```
apps/modules/
├── example/        # reference module — copy this to start a new module
├── warehouse/      # legacy reference (kept as working reference)
├── purchasing/     # legacy reference (kept as working reference)
└── inventory/      # legacy reference (kept as working reference)
```

## 2. Project Layout

```
project/
├── manage.py
├── requirements.txt
├── requirements-desktop.txt
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
├── config/
│   ├── urls.py
│   ├── api_urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── settings/
│       ├── base.py
│       ├── development.py
│       ├── test.py
│       ├── production.py
│       └── desktop.py
├── apps/
│   ├── core/
│   │   ├── models/  services/  repositories/  middleware/  permissions/
│   │   ├── validators/  utils/  constants/  exceptions/  management/
│   │   ├── admin.py  apps.py  context_processors.py  urls.py  api_urls.py
│   │   └── tests/
│   ├── accounts/
│   │   ├── models/  services/  views/  permissions/  management/
│   │   ├── urls.py  admin.py  apps.py
│   │   └── tests/
│   └── modules/
│       ├── example/
│       │   ├── models/  services/  repositories/  views/
│       │   ├── serializers/  forms/  permissions/  tests/
│       │   ├── urls.py  admin.py  apps.py
│       │   └── migrations/
│       └── ...
├── templates/
│   ├── base/  layouts/  pages/  components/  partials/  forms/  errors/  pdf/
├── static/
│   ├── css/  js/  fonts/  images/  vendor/
├── media/
├── tests/
│   ├── unit/  integration/  api/  e2e/
├── scripts/
│   ├── verify_api.py  check_static_refs.py  run.py  deploy.sh
│   └── maintenance/  restore/
├── deployment/
│   ├── docker/  nginx/  docker-compose.yml
├── desktop/
└── docs/
    ├── architecture/  development/  deployment/  api/  database/  security/
```

## 3. Module Dependency Rule

Dependencies flow **upwards only**:

```
Core
 ↑
Accounts
 ↑
Business Modules
```

- **Core** never imports from a business module.
- **Accounts** depends only on Core.
- **Business Modules** may depend on Core and Accounts.

## 4. Settings Architecture

Split by environment in `config/settings/`:

| Module | Purpose |
|--------|---------|
| `base.py` | Shared apps, middleware, templates, DB defaults, i18n, static/media, DRF, logging, env loading |
| `development.py` | `DEBUG=True`, dev tools, local configuration |
| `test.py` | Fast test database (in-memory SQLite where possible) |
| `production.py` | `DEBUG=False`, security flags, SSL/HSTS, secure cookies |
| `desktop.py` | PyInstaller compatibility, local paths, SQLite, offline |

`manage.py` auto-selects `config.settings.production` when `PORT` or `RENDER` is set,
otherwise `config.settings.development`.

## 5. Layering (Service Layer)

Complex business logic is never placed in views, forms, serializers, or templates.
Requests flow down through layers:

```
views
   ↓
services      (validation, business rules, transactions, audit, notifications)
   ↓
repositories  (query encapsulation)
   ↓
models/database
```

See `apps/modules/example/services/example_service.py` for the reference
implementation.

## 6. Error Handling

A unified exception hierarchy lives in `apps/core/utils/exceptions.py`:

```
AppError
 ├── ValidationError   (400)
 ├── PermissionDenied  (403)
 ├── NotFoundError     (404)
 ├── ConflictError     (409)
 ├── BusinessRuleError (422)
 └── SystemError       (500)
```

All API views funnel exceptions through `exception_to_response(...)`.
Server-rendered errors use `apps/core/views/handlers.py` (`handler404`,
`handler403`, `handler500`) registered in `config/urls.py`.

## 7. Core Components

- `BaseModel` — `created_at`, `updated_at`, `created_by`, `updated_by`
- `AuditLog` — generic audit trail (user, action, module, object, timestamp, IP, old/new value)
- `SystemSettings` — key/value runtime configuration with caching
- Common validators, exceptions, services, utilities
- `apps/core/utils/http.py` — `api_response`, `api_error`, `exception_to_response`, `paginate_queryset`, `api_response_paginated`
- `apps/core/utils/logging.py` — `security_logger`, `log_security_event(...)`
- `apps/core/services/system_settings.py` — cached settings access

## 8. Reusability Rules

- No business-specific fields or models inside `core`.
- A new project starts from Core + Accounts + Infrastructure + UI Components +
  Testing Infrastructure, then business modules are added per project.
- Semantic versioning (`MAJOR.MINOR.PATCH`), never tied to a business name.
