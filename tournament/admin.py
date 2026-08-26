import csv
from django.contrib import admin
from django.http import HttpResponse

from .models import (
    AuditEntry,
    Player,
    Team,
    TeamFanVote,
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name", "group_name", "cap_name", "cap_surname",
        "payment_status", "status", "checked_in",
    )
    list_filter = ("status", "payment_status", "group_name", "checked_in")
    search_fields = ("name", "cap_name", "cap_surname", "cap_email", "cap_phone", "blik_number")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Team Info", {"fields": ("name", "logo_path", "group_name", "status", "checked_in")}),
        ("Captain", {"fields": ("cap_name", "cap_surname", "cap_email", "cap_phone")}),
        ("Payment", {"fields": ("payment_status", "blik_number")}),
        ("Access", {"fields": ("roster_code",)}),
        ("MVP Entrance", {"fields": (
            "entrance_source", "entrance_url", "entrance_title",
            "entrance_artist", "entrance_artwork_url",
            "entrance_start_seconds", "entrance_duration_seconds"
        )}),
        ("Meta", {"fields": ("created_at",)}),
    )


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "team", "jersey_number", "position")
    list_filter = ("position", "team__group_name")
    search_fields = ("first_name", "last_name", "team__name", "jersey_number")


@admin.register(TeamFanVote)
class TeamFanVoteAdmin(admin.ModelAdmin):
    list_display = ("team", "email", "is_confirmed", "created_at")
    list_filter = ("team",)
    search_fields = ("email", "team__name")


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "category", "action", "entity_label")
    list_filter = ("category",)
    search_fields = ("action", "detail", "entity_label", "user__username")
    readonly_fields = ("timestamp", "user", "category", "action", "detail", "entity_type", "entity_id", "entity_label")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
