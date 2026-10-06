"""App config for مديول -1."""

from django.apps import AppConfig


class Module1Config(AppConfig):
    name = "apps.modules.module_1"
    verbose_name = "مديول -1"

    def ready(self):
        from apps.accounts.permissions.catalog import register_permissions

        from .permissions import GROUPS, PERMISSIONS

        register_permissions(PERMISSIONS, GROUPS)
