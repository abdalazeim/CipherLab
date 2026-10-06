"""Smoke tests for the مديول -1 module (CRUD + audit trail)."""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.core.models import AuditLog

from ..models import Module1Item

User = get_user_model()


@override_settings(ALLOWED_HOSTS=["*"])
class Module1ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", password="adminpass123"
        )
        self.client.login(username="admin", password="adminpass123")

    def _url(self, path):
        return "/api/modules/module_1" + path

    def test_list_empty(self):
        resp = self.client.get(self._url("/items/"))
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["items"], [])

    def test_stats(self):
        resp = self.client.get(self._url("/stats/"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])

    def test_create_item_logs_audit(self):
        resp = self.client.post(
            self._url("/items/create/"),
            data={"name": "عنصر", "code": "ABC-1", "quantity": 5},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Module1Item.objects.filter(code="ABC-1").exists())
        self.assertTrue(
            AuditLog.objects.filter(action="create", module="module_1").exists()
        )

    def test_create_duplicate_code_conflicts(self):
        Module1Item.objects.create(name="أ", code="DUP-1")
        resp = self.client.post(
            self._url("/items/create/"),
            data={"name": "ب", "code": "DUP-1"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_update_item(self):
        item = Module1Item.objects.create(name="قديم", code="UPD-1")
        resp = self.client.patch(
            self._url(f"/items/{item.pk}/update/"),
            data={"name": "جديد"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.name, "جديد")

    def test_delete_item(self):
        item = Module1Item.objects.create(name="حذف", code="DEL-1")
        resp = self.client.delete(self._url(f"/items/{item.pk}/delete/"))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Module1Item.objects.filter(pk=item.pk).exists())
