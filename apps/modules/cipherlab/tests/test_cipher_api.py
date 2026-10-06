import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.modules.cipherlab.models import CipherOperation


class CipherApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="cipher-admin", email="cipher@example.com", password="pass12345"
        )
        self.client.force_login(self.user)

    def test_operate_returns_result_and_saves_metadata_only(self):
        response = self.client.post(
            "/api/modules/cipherlab/operate/",
            data=json.dumps({
                "algorithm": "rot13",
                "operation": "encrypt",
                "text": "secret plaintext",
                "key": "private key",
                "parameter": "",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["result"], "frperg cynvagrkg")
        operation = CipherOperation.objects.get()
        self.assertEqual(operation.source_length, len("secret plaintext"))
        self.assertNotIn("secret plaintext", str(operation.__dict__))
        self.assertNotIn("private key", str(operation.__dict__))

    def test_anonymous_operation_is_rejected(self):
        self.client.logout()
        response = self.client.post(
            "/api/modules/cipherlab/operate/",
            data=json.dumps({"algorithm": "rot13", "operation": "encrypt", "text": "abc"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_cipher_input_whitespace_is_not_normalized(self):
        response = self.client.post(
            "/api/modules/cipherlab/operate/",
            data=json.dumps({
                "algorithm": "caesar",
                "operation": "encrypt",
                "text": "Meet Me At Six AM ",
                "parameter": "3",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["result"], "PhhwWPhWDwWVlaWDPW")

    def test_unsupported_algorithm_returns_validation_error(self):
        response = self.client.post(
            "/api/modules/cipherlab/operate/",
            data=json.dumps({"algorithm": "unknown", "operation": "encrypt", "text": "abc"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)