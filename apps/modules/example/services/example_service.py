"""Example module service layer.

Business logic lives here (not in views). Each operation is transactional and
optionally writes an audit entry, following the Master Template conventions.
"""

import logging

from django.db import transaction

from apps.core.services.audit_service import log_audit
from apps.core.utils.exceptions import BusinessRuleError, ConflictError

from ..models import ExampleItem
from ..repositories import ExampleItemRepository

logger = logging.getLogger("apps.api")

repository = ExampleItemRepository()


class ExampleItemService:
    """Service for :class:`~apps.modules.example.models.ExampleItem`."""

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
                module="example",
                object_id=str(item.pk),
                object_repr=item.name,
                new_value={"code": item.code, "name": item.name},
                user=user,
            )
        logger.info("Example item created: %s (%s)", item.name, item.code)
        return item

    def update(self, obj_id, request=None, *, user=None, data=None):
        item = repository.get_by_id(obj_id)
        old_value = {"code": item.code, "name": item.name}

        name = (data or {}).get("name")
        code = (data or {}).get("code")
        if code and repository.exists(code=code).exclude(pk=item.pk).exists():
            raise ConflictError("الكود مستخدم مسبقاً")

        with transaction.atomic():
            if name is not None:
                item.name = str(name).strip()
            if code is not None:
                item.code = str(code).strip()
            item.description = (data or {}).get("description", item.description)
            item.quantity = int((data or {}).get("quantity", item.quantity) or 0)
            item.sort_order = int((data or {}).get("sort_order", item.sort_order) or 0)
            item.save()
            log_audit(
                request,
                action="update",
                module="example",
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
                module="example",
                object_id=str(obj_id),
                object_repr=item.name,
                user=user,
            )
        return item

    def list(self, *, term="", page=1, page_size=20):
        qs = repository.search(term)
        return qs, repository.count()
