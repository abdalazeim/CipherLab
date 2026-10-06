from django.apps import AppConfig


class ExampleConfig(AppConfig):
    name = "apps.modules.example"
    verbose_name = "مثال عام"

    def ready(self):
        from apps.accounts.permissions.catalog import register_permissions

        from .permissions import GROUPS, PERMISSIONS

        register_permissions(PERMISSIONS, GROUPS)
