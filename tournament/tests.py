import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Team, Player

_STATIC_OVERRIDE = {
    "staticfiles": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

@override_settings(STORAGES=_STATIC_OVERRIDE, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationApiTests(TestCase):
    def setUp(self):
        self._media_dir = tempfile.TemporaryDirectory()
        self._media_override = self.settings(MEDIA_ROOT=self._media_dir.name)
        self._media_override.enable()

    def tearDown(self):
        self._media_override.disable()
        self._media_dir.cleanup()

    @staticmethod
    def _payload(team_name="Beach Blockers", email="beach.blockers@test.com"):
        return {
            "teamName": team_name,
            "capName": "Mila Stone",
            "phone": "+48111000222",
            "email": email,
            "players": json.dumps([
                {"firstName": "Mila", "lastName": "Stone"},
                {"firstName": "Nina", "lastName": "Hart"},
                {"firstName": "Luca", "lastName": "West"},
                {"firstName": "Adam", "lastName": "Shore"},
                {"firstName": "Kara", "lastName": "Vale"},
                {"firstName": "Noah", "lastName": "Drift"},
            ]),
            "lang": "en",
        }

    def test_register_accepts_multipart_logo_upload(self):
        url = reverse("api_register")
        logo = SimpleUploadedFile(
            "badge.png",
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 128,
            content_type="image/png",
        )

        payload = self._payload()
        payload["logo"] = logo
        response = self.client.post(url, payload)

        body = response.json()
        team = Team.objects.get(name="Beach Blockers")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertTrue(team.logo_path.endswith(".png"))
        self.assertEqual(team.players.count(), 6)

    @patch("tournament.views.send_mail", side_effect=RuntimeError("SMTP unavailable"))
    def test_registration_succeeds_when_payment_email_fails(self, _send_mail):
        response = self.client.post(
            reverse("api_register"),
            self._payload("Net Setters", "net.setters@test.com"),
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertFalse(body["email_sent"])
        self.assertTrue(Team.objects.filter(name="Net Setters").exists())

    def test_index_discovers_main_photo_with_case_insensitive_extension(self):
        page_dir = Path(self._media_dir.name) / "page"
        page_dir.mkdir()
        (page_dir / "main_photo.JPG").write_bytes(b"test-image")

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/media/page/main_photo.JPG')
        self.assertContains(response, 'hero-player-container--photo')
