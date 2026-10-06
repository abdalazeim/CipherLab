"""Generic dashboard statistics (domain-agnostic).

Business modules can contribute their own stats by registering a callback
via ``register_dashboard_stats_provider``. This keeps Core completely free
of any business domain knowledge.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone

from apps.core.models import AuditLog
from apps.core.utils.decorators import api_login_required

User = get_user_model()


_stats_providers = []


def register_stats_provider(callback):
    """Register a callable that returns a dict of extra stats for the dashboard."""
    _stats_providers.append(callback)


def _system_stats():
    return {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "total_audit_events": AuditLog.objects.count(),
        "audit_events_today": AuditLog.objects.filter(
            created_at__date=timezone.localdate()
        ).count(),
    }


def _latest_audit():
    return [
        {
            "id": entry.id,
            "action": entry.action,
            "action_label": entry.get_action_display(),
            "module": entry.module,
            "user_name": (
                entry.user.get_full_name() or entry.user.username
                if entry.user_id
                else ""
            ),
            "object_repr": entry.object_repr,
            "ip_address": entry.ip_address or "",
            "created_at": entry.created_at.isoformat(),
        }
        for entry in AuditLog.objects.select_related("user")[:10]
    ]


def _audit_activity():
    today = timezone.localdate()
    start_date = today - timedelta(days=6)
    daily_counts = {
        item["day"]: item["total"]
        for item in AuditLog.objects.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    }
    action_counts = dict(
        AuditLog.objects.filter(created_at__date__gte=start_date)
        .values_list("action")
        .annotate(total=Count("id"))
    )
    return {
        "audit_activity": [
            {"date": (start_date + timedelta(days=offset)).isoformat(), "total": daily_counts.get(start_date + timedelta(days=offset), 0)}
            for offset in range(7)
        ],
        "audit_actions": action_counts,
    }


@api_login_required
def dashboard_stats(request):
    stats = _system_stats()
    stats["latest_audit"] = _latest_audit()
    stats.update(_audit_activity())
    for provider in _stats_providers:
        try:
            stats.update(provider(request))
        except Exception:
            pass
    return JsonResponse(stats)
