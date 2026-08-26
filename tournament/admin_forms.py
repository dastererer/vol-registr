"""Forms for the custom admin panel."""

from django import forms
from django.forms import inlineformset_factory

from .models import Player, Team


class AdminTeamForm(forms.ModelForm):
    logo_upload = forms.FileField(
        required=False,
        label="Upload logo",
        help_text="JPG / PNG from your computer",
    )
    logo_url = forms.URLField(
        required=False,
        label="Logo URL",
        help_text="Or paste any direct image link",
    )

    class Meta:
        model = Team
        fields = [
            "name",
            "logo_path",
            "group_name",
            "cap_name",
            "cap_surname",
            "cap_email",
            "cap_phone",
            "payment_status",
            "blik_number",
            "status",
            "checked_in",
            "roster_code",
        ]
        widgets = {
            "logo_path": forms.TextInput(attrs={"readonly": "readonly", "style": "opacity:.6"}),
        }

    def clean(self):
        cleaned = super().clean()
        upload = cleaned.get("logo_upload")
        url = cleaned.get("logo_url")
        if upload and url:
            raise forms.ValidationError("Provide either a file or a URL, not both.")
        return cleaned


class AdminPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["first_name", "last_name"]
        widgets = {}


PlayerInlineFormSet = inlineformset_factory(
    Team,
    Player,
    form=AdminPlayerForm,
    extra=1,
    can_delete=True,
)
