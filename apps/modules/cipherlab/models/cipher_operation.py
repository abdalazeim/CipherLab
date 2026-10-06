from django.conf import settings
from django.db import models


class CipherOperation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="cipher_operations",
        null=True,
        blank=True,
    )
    algorithm = models.CharField(max_length=40, db_index=True)
    operation = models.CharField(max_length=10)
    source_length = models.PositiveIntegerField(default=0)
    result_length = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "cipherlab_operations"
        ordering = ["-created_at"]
        verbose_name = "عملية تشفير"
        verbose_name_plural = "عمليات التشفير"

    def __str__(self):
        return f"{self.algorithm} / {self.operation} ({self.created_at:%Y-%m-%d %H:%M})"