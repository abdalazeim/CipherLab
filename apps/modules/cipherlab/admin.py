from django.contrib import admin

from .models import CipherOperation


@admin.register(CipherOperation)
class CipherOperationAdmin(admin.ModelAdmin):
    list_display = ("algorithm", "operation", "user", "source_length", "result_length", "created_at")
    list_filter = ("algorithm", "operation", "created_at")
    search_fields = ("user__username",)
    readonly_fields = ("algorithm", "operation", "user", "source_length", "result_length", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False