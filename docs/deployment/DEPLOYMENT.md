# Deployment

## 1. Supported Targets

Local → Docker → Render → Linux VPS (Nginx + Gunicorn) → PostgreSQL / Neon.

## 2. Local

```bash
python manage.py runserver
# or
python scripts/run.py
```

Never use `runserver` in production.

## 3. Gunicorn

Config in `gunicorn.conf.py` (root) and `deployment/gunicorn/gunicorn.conf.py`:

- Binds `0.0.0.0:$PORT` (default `8000`)
- Workers = `cpu_count * 2 + 1` (override with `GUNICORN_WORKERS`)
- Sync worker class, timeout 120s, keepalive 5s
- Access logs include `x-forwarded-for`

```bash
gunicorn config.wsgi:application --config gunicorn.conf.py
```

## 4. Nginx (Reverse Proxy)

Config: `deployment/nginx/nginx.conf` (and `docker/nginx*.conf` for containers).

```
Client → Nginx → Gunicorn → Django → PostgreSQL
```

Responsibilities: HTTP/HTTPS termination, static files, media files, proxy to
Gunicorn.

## 5. Docker / Docker Compose

- `deployment/Dockerfile` + `deployment/docker/Dockerfile.prod`
- `deployment/docker/docker-compose.yml` (dev) and `docker-compose.prod.yml` (prod)
- Containers: `web`, `db`, `nginx`
- Entrypoints: `deployment/docker/scripts/entrypoint.sh`, `wait_for_db.sh`,
  `migrate.sh`, `collectstatic.sh`
- Makefile helpers: `deployment/docker/Makefile`

```bash
docker compose up -d --build
```

The system also runs without Docker during development (SQLite default).

## 6. Render

- `Procfile`:
  - `web: gunicorn config.wsgi:application --config gunicorn.conf.py`
  - `release: python manage.py migrate --noinput --settings=config.settings.production`
- `render.yaml` declares the web service.
- Set env vars in the Render dashboard (or `render.yaml`):
  `SECRET_KEY`, `DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
  `CORS_ALLOWED_ORIGINS`, `DATABASE_URL` (Neon, `sslmode=require`),
  `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`.
- `manage.py` auto-detects `PORT`/`RENDER` and uses production settings.

## 7. Linux VPS (systemd)

- Service unit: `deployment/gds.service` (paths `/opt/gds`).
- Script: `scripts/deploy.sh`.

## 8. Static & Media

```bash
python manage.py collectstatic --noinput
```

- `STATIC_ROOT = staticfiles/` — served via WhiteNoise in production.
- Media files: `media/` — must be persisted/backed up.

## 9. Health Checks for Platforms

| Endpoint | Purpose |
|----------|---------|
| `/health/` | app liveness (no DB) |
| `/health/db/` | DB readiness (503 on failure) |

Used by Render, Docker, load balancers and monitoring.

## 10. Backup & Recovery

See `docs/database/DATABASE.md`:

```bash
python manage.py backup_db
pg_dump --format=custom -f gds_backup.dump "postgresql://...?sslmode=require"
pg_restore --clean --if-exists -d "postgresql://...?sslmode=require" gds_backup.dump
```

Back up: database dump + `media/` + `.env`.

## 11. Production Security Quick Check

1. `DEBUG=False`
2. `SECRET_KEY` from env
3. HTTPS + secure cookies + HSTS (see `docs/security/SECURITY.md`)
4. `DJANGO_ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` set
5. Migrations applied via release step
6. `collectstatic` run

## 12. CI/CD

- `Jenkinsfile` — pipeline template.
- `.pre-commit-config.yaml` — local lint hooks.
- `pyproject.toml` — tooling config.
- Gate before merge: `check` + `makemigrations --check` + `test` +
  `verify_api.py` + `check_static_refs.py`.
