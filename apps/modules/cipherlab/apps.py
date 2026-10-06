from django.apps import AppConfig


class CipherLabConfig(AppConfig):
    name = "apps.modules.cipherlab"
    verbose_name = "مختبر التشفير"

    def ready(self):
        from apps.accounts.permissions.catalog import register_permissions

        from .permissions import GROUPS, PERMISSIONS

        register_permissions(PERMISSIONS, GROUPS)