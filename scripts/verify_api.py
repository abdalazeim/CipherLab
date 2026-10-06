import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django

django.setup()

from django.test import Client

c = Client()
c.get("/login/", HTTP_HOST="localhost")
r = c.post(
    "/api/auth/login",
    data=json.dumps({"username": "admin", "password": "admin123"}),
    content_type="application/json",
    HTTP_HOST="localhost",
)
print("login:", r.status_code, r.content.decode()[:120])

for path in [
    "/api/dashboard/stats",
    "/api/settings/lookups",
    "/api/settings/system",
    "/api/modules/example/items/",
]:
    resp = c.get(path, HTTP_HOST="localhost")
    body = resp.content.decode()
    summary = body[:140].replace("\n", " ")
    print(resp.status_code, path, "->", summary)
