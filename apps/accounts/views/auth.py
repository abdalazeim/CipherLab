import logging

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from apps.core.services.audit_service import log_audit
from apps.core.utils.decorators import api_login_required
from apps.core.utils.http import parse_json_body
from apps.core.utils.logging import log_security_event
from ..services.permission_service import get_effective_permissions


def _user_profile_dict(user):
    profile = getattr(user, "profile", None)
    return {
        "id": user.id,
        "name": user.get_full_name() or user.username,
        "username": user.username,
        "email": user.email,
        "phone": getattr(user, "phone", ""),
        "job_title": getattr(user, "job_title", ""),
        "department": getattr(user, "department", ""),
        "employee_number": getattr(user, "employee_number", ""),
        "role": "admin" if user.is_superuser else "user",
        "is_superuser": user.is_superuser,
        "permissions": get_effective_permissions(user),
        "system_role_name": (
            profile.system_role.name
            if profile and profile.system_role
            else ("مدير النظام" if user.is_superuser else "مستخدم")
        ),
        "group_name": profile.group.name if profile and profile.group else None,
        "group_id": profile.group_id if profile else None,
        "system_role_id": profile.system_role_id if profile else None,
    }


@csrf_exempt
@ensure_csrf_cookie
def auth_login(request):
    if request.method == "POST":
        data, err = parse_json_body(request)
        if err:
            return err
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if not username or not password:
            return JsonResponse(
                {"success": False, "error": "اسم المستخدم وكلمة المرور مطلوبان"},
                status=400,
            )
        # Validate password length to prevent DoS
        if len(password) > 128:
            return JsonResponse(
                {"success": False, "error": "كلمة المرور طويلة جداً"}, status=400
            )
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                log_security_event(
                    "login_disabled_account",
                    user=user,
                    request=request,
                    extra={"message": "حساب غير نشط"},
                )
                return JsonResponse(
                    {"success": False, "error": "الحساب غير نشط"}, status=403
                )
            login(request, user)
            log_audit(
                request,
                action="login",
                module="accounts",
                object_id=str(user.id),
                object_repr=user.username,
            )
            log_security_event(
                "login_success",
                user=user,
                request=request,
                level=logging.INFO,
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "تم تسجيل الدخول بنجاح",
                    "user": _user_profile_dict(user),
                }
            )
        log_security_event(
            "login_failed",
            request=request,
            extra={"username": username},
        )
        return JsonResponse(
            {"success": False, "error": "بيانات تسجيل الدخول غير صحيحة"}, status=401
        )
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)


@api_login_required
def auth_logout(request):
    log_audit(
        request,
        action="logout",
        module="accounts",
        object_id=str(request.user.id),
        object_repr=request.user.username,
    )
    log_security_event(
        "logout",
        user=request.user,
        request=request,
        level=logging.INFO,
    )
    logout(request)
    return JsonResponse({"success": True, "message": "تم تسجيل الخروج بنجاح"})


def auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {
                "logged_in": True,
                "user": _user_profile_dict(request.user),
            }
        )
    return JsonResponse({"logged_in": False})
