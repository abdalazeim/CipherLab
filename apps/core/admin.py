from django.contrib import admin

from .models import LookupCategory, SystemSetting


@admin.register(LookupCategory)
class LookupCategoryAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "sort_order", "is_active")
    list_filter = ("category", "is_active")


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("key",)
