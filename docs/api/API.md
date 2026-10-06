# API

## 1. Base URLs & Versioning

All endpoints are mounted twice from `config/api_urls.py`:

```
/api/          # default (kept for compatibility)
/api/v1/       # explicit versioned namespace
```

```
/api/v1/auth/login
/api/v1/auth/logout
/api/v1/auth/status
/api/v1/users
/api/v1/users/<id>
/api/v1/users/groups
/api/v1/users/roles
/api/v1/users/permissions
/api/v1/dashboard/stats
/api/v1/settings/...
/api/v1/backup/...
/api/v1/modules/example/items
```

A future `v2` is added by creating `config/api_v2_urls.py` and mounting it at
`/api/v2/` without breaking v1 consumers.

## 2. Unified Response Envelope

Every endpoint returns the same shape (helpers in `apps/core/utils/http.py`):

```json
{
  "success": true,
  "message": "...",
  "data": {},
  "errors": null
}
```

### Success

```json
{ "success": true, "message": "تم الحفظ", "data": { ... }, "errors": null }
```

### Failure

```json
{ "success": false, "message": "رسالة الخطأ", "data": null, "errors": [...] }
```

- `api_response(data, message, success, status, errors)` — success envelope.
- `api_error(message, status, errors)` — failure envelope (also mirrors
  `message` into `error` for backward compatibility).
- `api_response_paginated(items, meta, ...)` — paginated envelope:

```json
{
  "success": true,
  "message": "",
  "data": { "items": [...], "meta": { "page": 1, "page_size": 20, "total": 42,
                                      "pages": 3, "has_next": true, "has_previous": false } },
  "errors": null
}
```

Pagination query params: `?page=1&page_size=20` (`page_size` capped at 100).

## 3. Authentication

- **Login** — `POST /api/v1/auth/login` with `{ "username": "...", "password": "..." }`.
  Creates a Django session (session-based auth; the frontend uses cookies).
- **Logout** — `POST /api/v1/auth/logout`.
- **Status** — `GET /api/v1/auth/status` returns the current user and permissions.
- Login attempts are rate-limited (`RATE_LIMIT_LOGIN`, default `10/m`).
- Failed/successful logins are written to the security log
  (`log_security_event`).

## 4. Authorization

Views are protected with the `permission_required` decorator
(`apps/core/permissions`):

```python
@permission_required("example.manage", redirect_to_login=False)
def create_item(request):
    ...
```

Permissions are declared per module in `permissions/__init__.py`
(`PERMISSIONS` + `GROUPS`) and merged into a global `PERMISSION_REGISTRY` at app
startup. Denied requests produce the unified error envelope with 403.

## 5. Example Module Reference

`apps/modules/example/urls.py` (mounted at `/api/v1/modules/example/`):

| Method | Endpoint | Action | Permission |
|--------|----------|--------|------------|
| GET | `items/` | List/search (paginated) | `example_view` |
| POST | `items/create/` | Create | `example_manage` |
| GET | `items/<id>/` | Detail | `example_view` |
| POST | `items/<id>/update/` | Update | `example_manage` |
| POST | `items/<id>/delete/` | Delete | `example_manage` |

Copy this module to create new modules with identical conventions.

## 6. Health Checks

| Endpoint | Response |
|----------|----------|
| `GET /health/` | `{ "status": "ok", "service": "GDS-Template", "version": "1.0.0" }` |
| `GET /health/db/` | `{ "status": "...", "database": "ok", "error": null }` (503 on DB failure) |

Used by Render, Docker, load balancers and monitoring.

## 7. Error Handling

Unified exception hierarchy in `apps/core/utils/exceptions.py`:

| Exception | Status | Default message |
|-----------|--------|-----------------|
| `AppError` (base) | 400 | حدث خطأ |
| `ValidationError` | 400 | بيانات غير صالحة |
| `PermissionDenied` | 403 | ليس لديك صلاحية للوصول |
| `NotFoundError` | 404 | العنصر غير موجود |
| `ConflictError` | 409 | تعارض في البيانات |
| `BusinessRuleError` | 422 | لا يمكن تنفيذ العملية وفقاً للقواعد |
| `SystemError` | 500 | خطأ في النظام |

- `exception_to_response(exc)` (same module) converts any `AppError` into the
  unified `api_error` envelope.
- Non-API errors use `apps/core/views/handlers.py` (`handler404/403/500`),
  which return the same JSON envelope.
- Non-API errors use `apps/core/views/handlers.py` (`handler404/403/500`),
  which return the same JSON envelope.
