import uuid
from django.db import models

from .constants import (
    EMAIL_MAX_LENGTH,
    FREE_AGENT_NEW,
    FREE_AGENT_STATUS_CHOICES,
    GROUP_NAME_MAX_LENGTH,
    LOGO_PATH_MAX_LENGTH,
    PAYMENT_ACCEPTED,
    PAYMENT_STATUS_CHOICES,
    PAYMENT_WAITING,
    PERSON_NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    POSITION_CHOICES,
    TABLE_AUDIT_ENTRIES,
    TABLE_FREE_AGENT_APPLICATIONS,
    TABLE_PLAYERS,
    TABLE_TEAMS,
    TEAM_NAME_MAX_LENGTH,
    TEAM_STATUS_CHOICES,
    TEAM_STATUS_REGISTERED,
)


class Team(models.Model):
    """A registered tournament team with captain contact details."""

    name = models.CharField(
        max_length=TEAM_NAME_MAX_LENGTH, unique=True, verbose_name="Team Name"
    )
    logo_path = models.CharField(
        max_length=LOGO_PATH_MAX_LENGTH, blank=True, null=True
    )
    group_name = models.CharField(
        max_length=GROUP_NAME_MAX_LENGTH, blank=True, null=True
    )

    # Captain information
    cap_name = models.CharField(
        max_length=PERSON_NAME_MAX_LENGTH, verbose_name="Captain Name"
    )
    cap_surname = models.CharField(
        max_length=PERSON_NAME_MAX_LENGTH, verbose_name="Captain Surname"
    )
    cap_email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True)
    cap_phone = models.CharField(
        max_length=PHONE_MAX_LENGTH, unique=True, blank=True, null=True
    )

    payment_status = models.IntegerField(
        choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_WAITING
    )
    blik_number = models.CharField(
        max_length=20, blank=True, default="", verbose_name="Assigned BLIK"
    )
    status = models.CharField(
        max_length=20, choices=TEAM_STATUS_CHOICES, default=TEAM_STATUS_REGISTERED,
        verbose_name="Registration Status",
    )
    checked_in = models.BooleanField(default=False, verbose_name="Checked In")
    roster_code = models.CharField(
        max_length=10, blank=True, default="", verbose_name="Roster Access Code",
    )
    
    # Entrance Song (MVP)
    entrance_source = models.CharField(max_length=20, default="soundcloud", blank=True, null=True)
    entrance_url = models.URLField(max_length=500, blank=True, null=True)
    entrance_title = models.CharField(max_length=200, blank=True, null=True)
    entrance_artist = models.CharField(max_length=200, blank=True, null=True)
    entrance_artwork_url = models.URLField(max_length=500, blank=True, null=True)
    entrance_start_seconds = models.PositiveIntegerField(default=0)
    entrance_duration_seconds = models.PositiveIntegerField(default=15)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = TABLE_TEAMS
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_payment_status_display()})"

    # ── Readiness indicators ─────────────────────────────

    @property
    def is_payment_ok(self) -> bool:
        """Payment accepted."""
        return self.payment_status == PAYMENT_ACCEPTED

    @property
    def is_roster_complete(self) -> bool:
        """At least 6 players on the roster."""
        return self.players.count() >= 6

    @property
    def is_contacts_complete(self) -> bool:
        """Captain email AND phone are filled."""
        return bool(self.cap_email) and bool(self.cap_phone)

    @property
    def is_logo_uploaded(self) -> bool:
        """Team logo path is not empty."""
        return bool(self.logo_path)

    @property
    def readiness_target(self) -> int:
        """Number of active readiness checks used by the admin and panel UI."""
        return 4

    @property
    def has_duplicate_jerseys(self) -> bool:
        """Legacy jersey duplication check kept for compatibility with old stats data."""
        return False

    @property
    def readiness_score(self) -> int:
        """0-4 score: payment + roster + contacts + logo."""
        return sum([
            self.is_payment_ok,
            self.is_roster_complete,
            self.is_contacts_complete,
            self.is_logo_uploaded,
        ])


class Player(models.Model):
    """An individual player belonging to a team roster."""

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    first_name = models.CharField(max_length=PERSON_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=PERSON_NAME_MAX_LENGTH)
    jersey_number = models.CharField(max_length=3, blank=True, default="")
    position = models.CharField(
        max_length=3, choices=POSITION_CHOICES, blank=True, default="",
    )
    photo_path = models.CharField(
        max_length=LOGO_PATH_MAX_LENGTH, blank=True, default="",
    )

    class Meta:
        db_table = TABLE_PLAYERS

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ── Fan Voting ───────────────────────────────────────────

class TeamFanVote(models.Model):
    """Stores fan votes with email confirmation."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="fan_votes")
    email = models.EmailField(unique=True, help_text="One confirmed vote per email address.")
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_fan_votes"

    def __str__(self):
        return f"Vote for {self.team.name} by {self.email}"

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None


# ── Public Free-Agent Requests ───────────────────────────

class FreeAgentApplication(models.Model):
    """A no-account request from a player to a registered team captain."""

    first_name = models.CharField(max_length=PERSON_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=PERSON_NAME_MAX_LENGTH)
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="free_agent_applications",
    )
    message = models.TextField(max_length=1200)
    status = models.CharField(
        max_length=20,
        choices=FREE_AGENT_STATUS_CHOICES,
        default=FREE_AGENT_NEW,
        db_index=True,
    )
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = TABLE_FREE_AGENT_APPLICATIONS
        ordering = ["-created_at"]
        verbose_name = "Free-agent application"
        verbose_name_plural = "Free-agent applications"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} -> {self.team.name}"


# ── Audit ────────────────────────────────────────────────

AUDIT_CATEGORY_TEAM = "team"
AUDIT_CATEGORY_CHECKIN = "checkin"

AUDIT_CATEGORY_CHOICES = [
    (AUDIT_CATEGORY_TEAM, "Team"),
    (AUDIT_CATEGORY_CHECKIN, "Check-in"),
]


class AuditEntry(models.Model):
    """Tracks key operational events for audit timeline."""

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
    )
    category = models.CharField(max_length=20, choices=AUDIT_CATEGORY_CHOICES, db_index=True)
    action = models.CharField(max_length=120)
    detail = models.TextField(blank=True, default="")
    entity_type = models.CharField(max_length=40, blank=True, default="")
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    entity_label = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        db_table = TABLE_AUDIT_ENTRIES
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action}"

