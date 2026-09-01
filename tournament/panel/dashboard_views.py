"""Control Room for the currently supported registration operations."""

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from ..constants import (
    TEAM_STATUS_APPROVED,
    TEAM_STATUS_AWAITING_PAYMENT,
    TEAM_STATUS_PAID,
    TEAM_STATUS_REGISTERED,
)
from ..models import Player, Team


@staff_member_required(login_url="/panel/login/")
def dashboard_view(request):
    # ── KPI totals ────────────
    teams_total = Team.objects.count()
    teams_by_status = dict(
        Team.objects.values_list("status")
        .annotate(c=Count("id"))
        .values_list("status", "c")
    )
    players_total = Player.objects.count()

    # ── Check-in numbers ─────────────────────────────────
    approved_teams = Team.objects.filter(status=TEAM_STATUS_APPROVED)
    checkin_of = approved_teams.count()
    checkin_count = approved_teams.filter(checked_in=True).count()

    # ── Alerts ───────────────────────────────────────────
    alerts = []

    # Approved but not checked-in
    not_checked_in = approved_teams.filter(checked_in=False).count()
    if not_checked_in:
        alerts.append({
            "level": "warning",
            "icon": "fas fa-user-clock",
            "text": f"{not_checked_in} approved team(s) not checked in",
            "url": reverse("panel:checkin"),
        })

    # Teams awaiting payment
    awaiting_payment = Team.objects.filter(
        status=TEAM_STATUS_AWAITING_PAYMENT
    ).count()
    if awaiting_payment:
        alerts.append({
            "level": "warning",
            "icon": "fas fa-credit-card",
            "text": f"{awaiting_payment} team(s) awaiting payment",
            "url": f'{reverse("panel:teams")}?status={TEAM_STATUS_AWAITING_PAYMENT}',
        })

    # Paid but not yet approved
    paid_not_approved = Team.objects.filter(status=TEAM_STATUS_PAID).count()
    if paid_not_approved:
        alerts.append({
            "level": "info",
            "icon": "fas fa-check-circle",
            "text": f"{paid_not_approved} paid team(s) pending approval",
            "url": f'{reverse("panel:teams")}?status={TEAM_STATUS_PAID}',
        })

    # ── Queue cards ──────────────────────────────────────
    queues = []

    if not_checked_in:
        queues.append({
            "urgency": "warning",
            "icon": "fas fa-clipboard-check",
            "title": f"Check in {not_checked_in} team(s)",
            "detail": "Approved teams awaiting check-in",
            "url": reverse("panel:checkin"),
        })

    if awaiting_payment:
        queues.append({
            "urgency": "info",
            "icon": "fas fa-credit-card",
            "title": f"Review {awaiting_payment} payment(s)",
            "detail": "Teams awaiting payment confirmation",
            "url": f'{reverse("panel:teams")}?status={TEAM_STATUS_AWAITING_PAYMENT}',
        })

    incomplete_rosters = (
        Team.objects.annotate(player_count=Count("players"))
        .filter(player_count__lt=6)
        .count()
    )
    if incomplete_rosters:
        queues.append({
            "urgency": "warning",
            "icon": "fas fa-users",
            "title": f"Complete {incomplete_rosters} roster(s)",
            "detail": "Teams with fewer than six players",
            "url": f'{reverse("panel:teams")}?readiness=incomplete',
        })

    # ── Intelligence column ──────────────────────────────
    checkin_pct = (
        round(checkin_count / checkin_of * 100) if checkin_of > 0 else 0
    )

    recent_teams = Team.objects.order_by("-created_at")[:5]

    status_meta = [
        (TEAM_STATUS_REGISTERED, "Registered", "gray"),
        (TEAM_STATUS_AWAITING_PAYMENT, "Awaiting payment", "yellow"),
        (TEAM_STATUS_PAID, "Paid", "blue"),
        (TEAM_STATUS_APPROVED, "Approved", "green"),
    ]
    status_summary = []
    for status, label, color in status_meta:
        count = teams_by_status.get(status, 0)
        status_summary.append({
            "label": label,
            "count": count,
            "color": color,
            "pct": round(count / teams_total * 100) if teams_total else 0,
            "url": f'{reverse("panel:teams")}?status={status}',
        })

    ctx = {
        "page_title": "Control Room",
        "nav_section": "dashboard",
        # KPIs
        "teams_total": teams_total,
        "teams_by_status": teams_by_status,
        "players_total": players_total,
        "awaiting_payment": awaiting_payment,
        "checkin_count": checkin_count,
        "checkin_of": checkin_of,
        # Alerts
        "alerts": alerts,
        # Queues
        "queues": queues,
        "checkin_pct": checkin_pct,
        "status_summary": status_summary,
        "recent_teams": recent_teams,
    }
    return render(request, "panel/control_room.html", ctx)


@staff_member_required(login_url="/panel/login/")
def command_search(request):
    """Search the entities and pages that actually exist in the custom panel."""
    query = request.GET.get("q", "").strip()[:100]
    lowered = query.casefold()
    results = []

    pages = [
        ("Teams", "Team registration workflow", "fa-users", reverse("panel:teams")),
        ("Players", "Registered player directory", "fa-user", reverse("panel:players")),
        ("Check-in", "Tournament arrival desk", "fa-clipboard-check", reverse("panel:checkin")),
        ("Backups", "Database backup and restore", "fa-database", reverse("panel:db_backup")),
    ]
    for label, detail, icon, url in pages:
        if not lowered or lowered in label.casefold() or lowered in detail.casefold():
            results.append({"type": "page", "label": label, "detail": detail, "icon": icon, "url": url})

    if query:
        teams = Team.objects.filter(
            Q(name__icontains=query)
            | Q(cap_name__icontains=query)
            | Q(cap_surname__icontains=query)
        ).order_by("name")[:5]
        for team in teams:
            results.append({
                "type": "team",
                "label": team.name,
                "detail": f"Captain: {team.cap_name} {team.cap_surname}",
                "icon": "fa-shield-alt",
                "url": reverse("panel:team_detail", kwargs={"pk": team.pk}),
            })

        players = Player.objects.select_related("team").filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(team__name__icontains=query)
        ).order_by("last_name", "first_name")[:5]
        for player in players:
            results.append({
                "type": "player",
                "label": f"{player.first_name} {player.last_name}",
                "detail": player.team.name,
                "icon": "fa-user",
                "url": reverse("panel:player_detail", kwargs={"pk": player.pk}),
            })

    return JsonResponse({"results": results[:12]})
