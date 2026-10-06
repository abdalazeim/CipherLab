"""مديول -1 service layer (business logic + audit trail)."""

import logging

from django.db import transaction

from apps.core.services.audit_service import log_audit
from apps.core.utils.exceptions import BusinessRuleError, ConflictError

from ..models import Module1Item
from ..repositories import Module1ItemRepository

logger = logging.getLogger("apps.api")

repository = Module1ItemRepository()


class Module1ItemService:
    """Service for :class:`~apps.modules.module_1.models.Module1Item`."""

    def create(self, request=None, *, user=None, data=None):
        name = (data or {}).get("name", "").strip()
        code = (data or {}).get("code", "").strip()
        if not name or not code:
            raise BusinessRuleError("الاسم والكود مطلوبان")

        if repository.exists(code=code):
            raise ConflictError("الكود مستخدم مسبقاً")

        with transaction.atomic():
            item = repository.create(
                name=name,
                code=code,
                description=(data or {}).get("description", ""),
                quantity=int((data or {}).get("quantity", 0) or 0),
                sort_order=int((data or {}).get("sort_order", 0) or 0),
            )
            log_audit(
                request,
                action="create",
                module="module_1",
                object_id=str(item.pk),
                object_repr=item.name,
                new_value={"code": item.code, "name": item.name},
                user=user,
            )
        logger.info("%s created: %s (%s)", "Module1Item", item.name, item.code)
        return item

    def update(self, obj_id, request=None, *, user=None, data=None):
        item = repository.get_by_id(obj_id)
        old_value = {"code": item.code, "name": item.name}

        code = (data or {}).get("code")
        if code and repository.exists(code=code).exclude(pk=item.pk).exists():
            raise ConflictError("الكود مستخدم مسبقاً")

        with transaction.atomic():
            if (data or {}).get("name") is not None:
                item.name = str((data or {}).get("name")).strip()
            if code is not None:
                item.code = str(code).strip()
            item.description = (data or {}).get("description", item.description)
            item.quantity = int((data or {}).get("quantity", item.quantity) or 0)
            item.sort_order = int((data or {}).get("sort_order", item.sort_order) or 0)
            item.save()
            log_audit(
                request,
                action="update",
                module="module_1",
                object_id=str(item.pk),
                object_repr=item.name,
                old_value=old_value,
                new_value={"code": item.code, "name": item.name},
                user=user,
            )
        return item

    def delete(self, obj_id, request=None, *, user=None):
        item = repository.get_by_id(obj_id)
        with transaction.atomic():
            item.delete()
            log_audit(
                request,
                action="delete",
                module="module_1",
                object_id=str(obj_id),
                object_repr=item.name,
                user=user,
            )
        return item

    def stats(self):
        qs = repository.get_queryset()
        return {
            "total": qs.count(),
            "active": qs.filter(is_active=True).count(),
        }
