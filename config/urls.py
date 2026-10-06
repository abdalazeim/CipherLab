import sys
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve


def is_frozen():
    return getattr(sys, "frozen", False)


def get_bundle_dir():
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_app_dir():
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


urlpatterns = [
    path("admin/", admin.site.urls),
    # Pages (non-API)
    path("", include("apps.core.urls")),
    # API: legacy (default) and explicit versioned v1
    path("api/", include("config.api_urls")),
    path("api/v1/", include(("config.api_urls", "api"), namespace="api_v1")),
]

handler404 = "apps.core.views.handlers.handler404"
handler403 = "apps.core.views.handlers.handler403"
handler500 = "apps.core.views.handlers.handler500"

if is_frozen():
    bundle_static = get_bundle_dir() / "static"
    if bundle_static.exists():
        urlpatterns += [
            path("static/<path:path>", serve, {"document_root": str(bundle_static)}),
        ]

    app_staticfiles = get_app_dir() / "staticfiles"
    if app_staticfiles.exists():
        urlpatterns += [
            path("static/<path:path>", serve, {"document_root": str(app_staticfiles)}),
        ]

    bundle_staticfiles = get_bundle_dir() / "staticfiles"
    if bundle_staticfiles.exists() and str(bundle_staticfiles) != str(app_staticfiles):
        urlpatterns += [
            path(
                "static/<path:path>", serve, {"document_root": str(bundle_staticfiles)}
            ),
        ]
else:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    for static_dir in settings.STATICFILES_DIRS:
        if static_dir.exists():
            urlpatterns += [
                path("static/<path:path>", serve, {"document_root": str(static_dir)}),
            ]
