from django.contrib import admin

from .models import Module1Item


@admin.register(Module1Item)
class Module1ItemAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "quantity", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")
