from django.views.decorators.http import require_GET, require_POST

from apps.core.utils.decorators import api_login_required, api_permission_required
from apps.core.utils.http import api_error, api_response, parse_json_body

from ..forms import CipherOperationForm
from ..models import CipherOperation
from ..services import CipherService, LegacyCipherError


@require_GET
@api_login_required
@api_permission_required("cipherlab_view")
def algorithm_catalog(request):
    algorithms = [{"id": key, "name": value} for key, value in CipherService.ALGORITHMS.items()]
    return api_response(algorithms, message="تم تحميل الخوارزميات")


@require_POST
@api_login_required
@api_permission_required("cipherlab_operate")
def operate(request):
    data, error = parse_json_body(request)
    if error:
        return error
    form = CipherOperationForm(data)
    if not form.is_valid():
        return api_error("بيانات العملية غير صالحة", status=400, errors=form.errors.get_json_data())
    cleaned = form.cleaned_data
    try:
        result = CipherService.operate(
            cleaned["algorithm"],
            cleaned["operation"],
            cleaned["text"],
            key=cleaned["key"],
            parameter=cleaned["parameter"],
        )
    except LegacyCipherError as exc:
        return api_error(str(exc), status=422)
    CipherOperation.objects.create(
        user=request.user,
        algorithm=cleaned["algorithm"],
        operation=cleaned["operation"],
        source_length=len(cleaned["text"]),
        result_length=len(result),
    )
    return api_response({"result": result}, message="اكتملت العملية")


@require_GET
@api_login_required
@api_permission_required("cipherlab_view")
def history(request):
    operations = CipherOperation.objects.select_related("user")[:30]
    data = [
        {
            "algorithm": CipherService.ALGORITHMS.get(item.algorithm, item.algorithm),
            "operation": item.operation,
            "user": item.user.get_username() if item.user else "",
            "source_length": item.source_length,
            "result_length": item.result_length,
            "created_at": item.created_at.isoformat(),
        }
        for item in operations
    ]
    return api_response(data, message="تم تحميل سجل العمليات")