"""Central API route table.

All API endpoints are registered here without the ``api/`` prefix and
mounted twice from ``config/urls.py``:

- ``/api/``    -> legacy/default version (keeps the existing frontend working)
- ``/api/v1/`` -> explicit versioned namespace

Business modules should register their URLs here when added to the project.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.api_urls")),
    path("", include("apps.accounts.urls")),
    path("modules/example/", include("apps.modules.example.urls")),
    path("modules/module_1/", include("apps.modules.module_1.urls")),
    path("modules/cipherlab/", include("apps.modules.cipherlab.urls")),
]
