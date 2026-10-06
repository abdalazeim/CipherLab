"""مديول -1 module API views (CRUD + stats)."""

from apps.core.utils.decorators import api_login_required, api_permission_required
from apps.core.utils.exceptions import AppError, exception_to_response
from apps.core.utils.http import (
    api_error,
    api_response,
    api_response_paginated,
    parse_json_body,
    paginate_queryset,
)

from ..repositories import Module1ItemRepository
from ..serializers import serialize_module_1_item, serialize_module_1_item_list
from ..services import Module1ItemService

service = Module1ItemService()
repository = Module1ItemRepository()


@api_login_required
@api_permission_required("module_1_view")
def list_items(request):
    term = request.GET.get("q", "").strip()
    page_obj, meta = paginate_queryset(
        repository.search(term),
        request,
        page_size=int(request.GET.get("page_size", 20)),
    )
    return api_response_paginated(
        serialize_module_1_item_list(list(page_obj)), meta, message="تم تحميل القائمة"
    )


@api_login_required
@api_permission_required("module_1_view")
def module_stats(request):
    return api_response(service.stats(), message="تم تحميل الإحصائيات")


@api_login_required
@api_permission_required("module_1_manage")
def create_item(request):
    if request.method != "POST":
        return api_error("Method not allowed", status=405)
    data, err = parse_json_body(request)
    if err:
        return err
    try:
        item = service.create(request, data=data)
        return api_response(
            serialize_module_1_item(item), message="تم الإنشاء بنجاح", status=201
        )
    except AppError as exc:
        return exception_to_response(exc)


@api_login_required
@api_permission_required("module_1_manage")
def update_item(request, item_id):
    if request.method not in ("PUT", "PATCH"):
        return api_error("Method not allowed", status=405)
    data, err = parse_json_body(request)
    if err:
        return err
    try:
        item = service.update(item_id, request, data=data)
        return api_response(serialize_module_1_item(item), message="تم التحديث بنجاح")
    except AppError as exc:
        return exception_to_response(exc)


@api_login_required
@api_permission_required("module_1_manage")
def delete_item(request, item_id):
    if request.method != "DELETE":
        return api_error("Method not allowed", status=405)
    try:
        service.delete(item_id, request)
        return api_response(message="تم الحذف بنجاح")
    except AppError as exc:
        return exception_to_response(exc)


@api_login_required
@api_permission_required("module_1_view")
def get_item(request, item_id):
    try:
        item = repository.get_by_id(item_id)
        return api_response(serialize_module_1_item(item))
    except AppError as exc:
        return exception_to_response(exc)
