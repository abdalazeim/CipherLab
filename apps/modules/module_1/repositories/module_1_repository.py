"""مديول -1 repository (data-access layer)."""

from django.db.models import Q

from apps.core.repositories import BaseRepository

from ..models import Module1Item


class Module1ItemRepository(BaseRepository):
    model = Module1Item

    def search(self, term=""):
        qs = self.get_queryset()
        if term:
            qs = qs.filter(Q(name__icontains=term) | Q(code__icontains=term))
        return qs
