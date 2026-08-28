"""Validated public forms for tournament registration and player requests."""

from django import forms

from .constants import FREE_AGENT_NEW, PAYMENT_REFUND
from .models import FreeAgentApplication, Team


class PlayerForm(forms.Form):
    """Validates a single player entry in the roster."""

    firstName = forms.CharField(max_length=50, strip=True)
    lastName = forms.CharField(max_length=50, strip=True)


class TeamRegistrationForm(forms.Form):
    """Validates the JSON payload sent from the 3-step registration page."""

    # ── Step 1: Team Identity ───────────────────────────────
    teamName = forms.CharField(max_length=100, strip=True)

    # ── Step 2: Captain ─────────────────────────────────────
    capName = forms.CharField(max_length=100, strip=True)
    phone = forms.CharField(max_length=20, required=False, strip=True)
    email = forms.EmailField(max_length=100)

    # ── Entrance Song ───────────────────────────────────────
    entranceUrl = forms.URLField(max_length=500, required=False)
    entranceTitle = forms.CharField(max_length=200, required=False)
    entranceArtist = forms.CharField(max_length=200, required=False)
    entranceArtworkUrl = forms.URLField(max_length=500, required=False)
    entranceSource = forms.CharField(max_length=20, required=False)
    entranceStartSeconds = forms.IntegerField(required=False, initial=0)

    def clean_capName(self):
        """Split full name into (first, last) dict stored in cleaned_data."""
        full_name = self.cleaned_data["capName"]
        parts = full_name.split(" ", 1)
        return {
            "first": parts[0],
            "last": parts[1] if len(parts) > 1 else "",
        }


# ── Public Free-Agent Request ────────────────────────────

class FreeAgentApplicationForm(forms.ModelForm):
    """No-account application delivered to the selected team captain."""

    privacy = forms.BooleanField(
        required=True,
        label="I agree that my contact details can be sent to the selected team captain.",
    )

    class Meta:
        model = FreeAgentApplication
        fields = ["first_name", "last_name", "email", "team", "message"]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email",
            "team": "Team",
            "message": "Message to the captain",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name", "placeholder": "Maksym"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name", "placeholder": "Kotsiubailo"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}),
            "team": forms.Select(),
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "maxlength": 1200,
                    "placeholder": "Tell the captain about your experience, position and availability.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team"].queryset = Team.objects.exclude(
            payment_status=PAYMENT_REFUND
        ).order_by("name")
        self.fields["team"].empty_label = "Choose a registered team"

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        team = cleaned.get("team")
        if email and team and FreeAgentApplication.objects.filter(
            email__iexact=email,
            team=team,
            status=FREE_AGENT_NEW,
        ).exists():
            raise forms.ValidationError(
                "You already have an open request for this team. The captain has your message."
            )
        return cleaned
