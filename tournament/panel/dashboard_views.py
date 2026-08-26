"""Control Room — operational dashboard replacing the old KPI page."""

import datetime as _dt

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from ..constants import (
    TEAM_STATUS_APPROVED,
    TEAM_STATUS_AWAITING_PAYMENT,
    TEAM_STATUS_PAID,
)
from ..models import Player, Team


@staff_member_required(login_url="/panel/login/")
def dashboard_view(request):
    now = timezone.now()

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
            "url": "/panel/checkin/",
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
            "url": "/panel/teams/?status=AWAITING_PAYMENT",
        })

    # Paid but not yet approved
    paid_not_approved = Team.objects.filter(status=TEAM_STATUS_PAID).count()
    if paid_not_approved:
        alerts.append({
            "level": "info",
            "icon": "fas fa-check-circle",
            "text": f"{paid_not_approved} paid team(s) pending approval",
            "url": "/panel/teams/?status=PAID",
        })

    # ── Queue cards ──────────────────────────────────────
    queues = []

    if not_checked_in:
        queues.append({
            "urgency": "warning",
            "icon": "fas fa-clipboard-check",
            "title": f"Check in {not_checked_in} team(s)",
            "detail": "Approved teams awaiting check-in",
            "url": "/panel/checkin/",
        })

    if awaiting_payment:
        queues.append({
            "urgency": "info",
            "icon": "fas fa-credit-card",
            "title": f"Review {awaiting_payment} payment(s)",
            "detail": "Teams awaiting payment confirmation",
            "url": "/panel/teams/?status=AWAITING_PAYMENT",
        })

    # ── Intelligence column ──────────────────────────────
    checkin_pct = (
        round(checkin_count / checkin_of * 100) if checkin_of > 0 else 0
    )

    recent_teams = Team.objects.order_by("-created_at")[:5]

    ctx = {
        "page_title": "Control Room",
        "nav_section": "dashboard",
        # KPIs
        "teams_total": teams_total,
        "teams_by_status": teams_by_status,
        "players_total": players_total,
        "checkin_count": checkin_count,
        "checkin_of": checkin_of,
        # Alerts
        "alerts": alerts,
        # Queues
        "queues": queues,
        # Timeline
        "now": now,
        # Intelligence
        "checkin_pct": checkin_pct,
        # Recent
        "recent_teams": recent_teams,
    }
    return render(request, "panel/control_room.html", ctx)
