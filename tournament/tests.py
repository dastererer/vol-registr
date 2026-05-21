import json
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Team, Player

_STATIC_OVERRIDE = {
    "staticfiles": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

@override_settings(STORAGES=_STATIC_OVERRIDE, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationApiTests(TestCase):
    def test_register_accepts_multipart_logo_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        url = reverse("api_register")
        logo = SimpleUploadedFile(
            "badge.png",
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 128,
            content_type="image/png",
        )

        response = self.client.post(url, {
            "teamName": "Beach Blockers",
            "capName": "Mila Stone",
            "phone": "+48111000222",
            "email": "beach.blockers@test.com",
            "players": json.dumps([
                {"firstName": "Mila", "lastName": "Stone"},
                {"firstName": "Nina", "lastName": "Hart"},
                {"firstName": "Luca", "lastName": "West"},
                {"firstName": "Adam", "lastName": "Shore"},
                {"firstName": "Kara", "lastName": "Vale"},
                {"firstName": "Noah", "lastName": "Drift"},
            ]),
            "lang": "en",
            "logo": logo,
        })

        body = response.json()
        team = Team.objects.get(name="Beach Blockers")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["success"])
        self.assertTrue(team.logo_path.endswith(".png"))
        self.assertEqual(team.players.count(), 6)
