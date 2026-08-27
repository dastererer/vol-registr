"""
Django forms for tournament team registration and the platform account layer.

Handles input validation and sanitization
before data reaches the service layer.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .constants import PIZZA_CHOICES, POSITION_CHOICES
from .models import (
    PizzaOrder,
    PlayerProfile,
    Team,
    TeamApplication,
    TeamInvite,
)


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


# ── Auth & Player Profile ────────────────────────────────────────────────────

class SignUpForm(UserCreationForm):
    """Frictionless signup — email is required."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False, strip=True)
    last_name = forms.CharField(max_length=50, required=False, strip=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email


class PlayerProfileForm(forms.ModelForm):
    """Editable player identity."""

    class Meta:
        model = PlayerProfile
        fields = ["display_name", "position", "photo", "phone", "is_free_agent"]
        widgets = {
            "display_name": forms.TextInput(attrs={"placeholder": "How you want to appear on your card"}),
            "phone": forms.TextInput(attrs={"placeholder": "Contact phone"}),
        }


# ── Team Engine ──────────────────────────────────────────────────────────────

class TeamCreateForm(forms.ModelForm):
    """Create a new team and become its captain."""

    class Meta:
        model = Team
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Team name"}),
        }


class TeamApplicationForm(forms.ModelForm):
    """Ask to join a team."""

    class Meta:
        model = TeamApplication
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Tell the captain why you want to join..."}
            ),
        }


class TeamInviteForm(forms.ModelForm):
    """Captain recruits a free agent."""

    class Meta:
        model = TeamInvite
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Why should they join your team?"}
            ),
        }


class PizzaOrderForm(forms.ModelForm):
    """Captain pre-orders pizzas for game day."""

    class Meta:
        model = PizzaOrder
        fields = ["pizza_type", "quantity"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1, "max": 99}),
        }

