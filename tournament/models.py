import uuid
from django.conf import settings
from django.db import models

from .constants import (
    APPLICATION_STATUS_CHOICES,
    APPLICATION_PENDING,
    EMAIL_MAX_LENGTH,
    GROUP_NAME_MAX_LENGTH,
    INVITE_STATUS_CHOICES,
    INVITE_PENDING,
    LOGO_PATH_MAX_LENGTH,
    PAYMENT_ACCEPTED,
    PAYMENT_STATUS_CHOICES,
    PAYMENT_WAITING,
    PERSON_NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    PIZZA_CHOICES,
    POSITION_CHOICES,
    TABLE_AUDIT_ENTRIES,
    TABLE_HIGHLIGHTS,
    TABLE_PIZZA_ORDERS,
    TABLE_PLAYER_PROFILES,
    TABLE_PLAYERS,
    TABLE_POWER_RANKING_ARTICLES,
    TABLE_TEAM_APPLICATIONS,
    TABLE_TEAM_INVITES,
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

    # Platform account link (legacy cap_* fields retained for compatibility)
    captain_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="captained_teams",
        verbose_name="Captain User Account",
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

    # Optional link to the new PlayerProfile platform entity
    profile = models.ForeignKey(
        "PlayerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legacy_players",
        verbose_name="Player Profile",
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


# ── Platform Accounts & Rosters ───────────────────────────────────────────────

class PlayerProfile(models.Model):
    """Persistent player identity tied to a Django user account."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player_profile",
    )
    display_name = models.CharField(
        max_length=PERSON_NAME_MAX_LENGTH * 2 + 1,
        blank=True,
        default="",
        verbose_name="Display Name",
    )
    position = models.CharField(
        max_length=3,
        choices=POSITION_CHOICES,
        blank=True,
        default="",
        verbose_name="Position",
    )
    photo = models.ImageField(
        upload_to="player_photos/",
        blank=True,
        null=True,
        verbose_name="Player Photo",
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        default="",
        verbose_name="Contact Phone",
    )
    is_free_agent = models.BooleanField(
        default=False,
        verbose_name="Free Agent",
        help_text="Visible on the public Free Agent board.",
    )

    # Current roster membership (null = free agent)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_profiles",
        verbose_name="Current Team",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = TABLE_PLAYER_PROFILES
        verbose_name = "Player Profile"
        verbose_name_plural = "Player Profiles"

    def __str__(self) -> str:
        return self.display_name or self.user.username

    @property
    def full_name(self) -> str:
        return self.display_name or self.user.get_full_name() or self.user.username


class TeamApplication(models.Model):
    """A player asks to join a team; the captain accepts or rejects."""

    profile = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    message = models.TextField(
        blank=True,
        default="",
        verbose_name="Message to Captain",
    )
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default=APPLICATION_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = TABLE_TEAM_APPLICATIONS
        unique_together = [["profile", "team"]]
        ordering = ["-created_at"]
        verbose_name = "Team Application"
        verbose_name_plural = "Team Applications"

    def __str__(self) -> str:
        return f"{self.profile} -> {self.team.name} ({self.status})"


class TeamInvite(models.Model):
    """A captain invites a free agent to join their team."""

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    profile = models.ForeignKey(
        PlayerProfile,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    message = models.TextField(
        blank=True,
        default="",
        verbose_name="Recruiting Message",
    )
    status = models.CharField(
        max_length=20,
        choices=INVITE_STATUS_CHOICES,
        default=INVITE_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = TABLE_TEAM_INVITES
        unique_together = [["team", "profile"]]
        ordering = ["-created_at"]
        verbose_name = "Team Invite"
        verbose_name_plural = "Team Invites"

    def __str__(self) -> str:
        return f"{self.team.name} -> {self.profile} ({self.status})"


class PizzaOrder(models.Model):
    """Captain pre-orders discounted pizzas for a team."""

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="pizza_orders",
    )
    pizza_type = models.CharField(
        max_length=30,
        choices=PIZZA_CHOICES,
        verbose_name="Pizza",
    )
    quantity = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = TABLE_PIZZA_ORDERS
        ordering = ["-created_at"]
        verbose_name = "Pizza Order"
        verbose_name_plural = "Pizza Orders"

    def __str__(self) -> str:
        return f"{self.quantity}x {self.pizza_type} for {self.team.name}"



# ── Media & Hype ──────────────────────────────────────────────────────────────

class PowerRankingArticle(models.Model):
    """Pre-tournament hype article ranking teams."""

    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Rich text content. Use Markdown or HTML.")
    publish_date = models.DateTimeField(db_index=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = TABLE_POWER_RANKING_ARTICLES
        ordering = ["-publish_date"]
        verbose_name = "Power Ranking Article"
        verbose_name_plural = "Power Ranking Articles"

    def __str__(self) -> str:
        return self.title


class Highlight(models.Model):
    """External video highlight shared by authenticated users."""

    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="highlights",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = TABLE_HIGHLIGHTS
        ordering = ["-created_at"]
        verbose_name = "Highlight"
        verbose_name_plural = "Highlights"

    def __str__(self) -> str:
        return self.title

    @property
    def domain(self) -> str:
        from urllib.parse import urlparse
        return urlparse(self.url).netloc.replace("www.", "")

