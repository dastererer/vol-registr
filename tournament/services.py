"""
Business-logic layer for tournament registration.
"""

from __future__ import annotations

import logging

from django.db import transaction

from .constants import (
    MAX_TOURNAMENT_SLOTS,
    PAYMENT_ACCEPTED,
    PAYMENT_WAITING,
)
from .models import (
    Player,
    Team,
)

logger = logging.getLogger(__name__)

def get_available_slots() -> int:
    """Return remaining open slots based on accepted teams."""
    approved = Team.objects.filter(payment_status=PAYMENT_ACCEPTED).count()
    return max(MAX_TOURNAMENT_SLOTS - approved, 0)

@transaction.atomic
def register_team(cleaned: dict, players_data: list[dict] | None = None) -> Team:
    team_name = cleaned["teamName"]
    email = cleaned["email"]
    cap = cleaned["capName"]

    if Team.objects.filter(name=team_name).exists():
        raise ValueError("Team name already taken.")

    if Team.objects.filter(cap_email=email).exists():
        raise ValueError("This email is already registered.")

    phone = cleaned.get("phone") or None
    if phone and Team.objects.filter(cap_phone=phone).exists():
        raise ValueError("This phone number is already registered.")

    team = Team.objects.create(
        name=team_name,
        cap_name=cap["first"],
        cap_surname=cap["last"],
        cap_phone=phone,
        cap_email=email,
        payment_status=PAYMENT_WAITING,
        entrance_url=cleaned.get("entranceUrl") or None,
        entrance_title=cleaned.get("entranceTitle") or None,
        entrance_artist=cleaned.get("entranceArtist") or None,
        entrance_artwork_url=cleaned.get("entranceArtworkUrl") or None,
        entrance_source=cleaned.get("entranceSource") or "soundcloud",
        entrance_start_seconds=cleaned.get("entranceStartSeconds") or 0,
    )

    if players_data:
        _create_players(team, players_data)

    return team

def _create_players(team: Team, players_data: list[dict]) -> None:
    from .forms import PlayerForm

    players_to_create: list[Player] = []
    for entry in players_data:
        form = PlayerForm(entry)
        if not form.is_valid():
            continue

        cd = form.cleaned_data
        first = cd.get("firstName", "").strip()
        if not first:
            continue

        players_to_create.append(
            Player(
                team=team,
                first_name=first,
                last_name=cd.get("lastName", "").strip(),
            )
        )

    if players_to_create:
        Player.objects.bulk_create(players_to_create)
