import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .constants import MAX_TOURNAMENT_SLOTS, PAYMENT_REFUND
from .models import FreeAgentApplication, Team
from .services import get_available_slots

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
        self.assertContains(response, 'hero-bg-swiper')

    def test_registration_rejects_a_team_after_all_slots_are_reserved(self):
        Team.objects.bulk_create(
            [
                Team(
                    name=f"Reserved {index}",
                    cap_name="Captain",
                    cap_surname=str(index),
                    cap_email=f"reserved-{index}@example.com",
                )
                for index in range(MAX_TOURNAMENT_SLOTS)
            ]
        )

        response = self.client.post(
            reverse("api_register"),
            self._payload("One Too Many", "overflow@example.com"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Tournament registration is full.")
        self.assertEqual(Team.objects.count(), MAX_TOURNAMENT_SLOTS)


@override_settings(STORAGES=_STATIC_OVERRIDE, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PublicPlatformRethinkTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name="Block Party",
            cap_name="Marta",
            cap_surname="Nowak",
            cap_email="captain@example.com",
            cap_phone="+48123123123",
        )

    def _free_agent_payload(self, email="player@example.com"):
        return {
            "first_name": "Alicja",
            "last_name": "Kowalska",
            "email": email,
            "team": self.team.pk,
            "message": "Gram na przyjęciu i mogę być na całym turnieju.",
            "privacy": "on",
        }

    def test_free_agent_form_is_public(self):
        response = self.client.get(reverse("platform:free_agents"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Need a team?")
        self.assertContains(response, self.team.name)

    def test_waiting_registration_reserves_a_slot_and_refund_releases_it(self):
        self.assertEqual(get_available_slots(), MAX_TOURNAMENT_SLOTS - 1)

        index_response = self.client.get(reverse("index"))
        self.assertEqual(index_response.context["registered_teams"], 1)

        self.team.payment_status = PAYMENT_REFUND
        self.team.save(update_fields=["payment_status"])
        self.assertEqual(get_available_slots(), MAX_TOURNAMENT_SLOTS)

        free_agent_response = self.client.get(reverse("platform:free_agents"))
        self.assertNotContains(free_agent_response, self.team.name)

    def test_free_agent_request_is_saved_and_emailed_to_captain(self):
        response = self.client.post(
            reverse("platform:free_agents"),
            self._free_agent_payload(),
        )

        application = FreeAgentApplication.objects.get()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["submitted"])
        self.assertTrue(application.email_sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.team.cap_email])
        self.assertEqual(mail.outbox[0].reply_to, [application.email])

    @patch("tournament.platform_views.EmailMessage.send", side_effect=RuntimeError("SMTP unavailable"))
    def test_free_agent_request_survives_email_failure(self, _send):
        response = self.client.post(
            reverse("platform:free_agents"),
            self._free_agent_payload("deferred@example.com"),
        )

        application = FreeAgentApplication.objects.get(email="deferred@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["submitted"])
        self.assertTrue(response.context["delivery_deferred"])
        self.assertFalse(application.email_sent)

    def test_duplicate_open_free_agent_request_is_rejected(self):
        payload = self._free_agent_payload()
        first_response = self.client.post(reverse("platform:free_agents"), payload)
        second_response = self.client.post(reverse("platform:free_agents"), payload)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertFalse(second_response.context["submitted"])
        self.assertContains(second_response, "already have", status_code=200)
        self.assertEqual(FreeAgentApplication.objects.count(), 1)

    def test_canonical_team_page_replaces_duplicate_platform_url(self):
        canonical_url = reverse("tournament_team", args=[self.team.pk])

        canonical_response = self.client.get(canonical_url)
        legacy_response = self.client.get(
            reverse("platform:team_detail", args=[self.team.pk])
        )

        self.assertEqual(canonical_response.status_code, 200)
        self.assertContains(canonical_response, self.team.name)
        self.assertRedirects(
            legacy_response,
            canonical_url,
            fetch_redirect_response=False,
        )

    def test_retired_platform_pages_redirect_to_active_flows(self):
        redirects = {
            reverse("platform:team_list"): f'{reverse("index")}#registeredTeamsModal',
            reverse("platform:profile"): reverse("roster_update"),
            reverse("platform:rankings"): reverse("index"),
            reverse("platform:live_feed"): reverse("index"),
        }

        for source, target in redirects.items():
            with self.subTest(source=source):
                self.assertRedirects(
                    self.client.get(source),
                    target,
                    fetch_redirect_response=False,
                )
