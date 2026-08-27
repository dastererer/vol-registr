"""Platform views: accounts, rosters, free agents, player cards, sponsor pizza orders."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .constants import (
    APPLICATION_ACCEPTED,
    APPLICATION_PENDING,
    APPLICATION_REJECTED,
    INVITE_ACCEPTED,
    INVITE_PENDING,
    INVITE_REJECTED,
    PIZZA_CHOICES,
    PIZZERIA_KULTOWA,
    POSITION_CHOICES,
)
from .forms import (
    PizzaOrderForm,
    PlayerProfileForm,
    SignUpForm,
    TeamApplicationForm,
    TeamCreateForm,
    TeamInviteForm,
)
from .models import (
    PizzaOrder,
    PlayerProfile,
    Team,
    TeamApplication,
    TeamInvite,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_profile(user):
    profile, _ = PlayerProfile.objects.get_or_create(user=user)
    return profile


def _is_captain(user, team):
    return user.is_authenticated and team.captain_user_id == user.id


# ── Auth ─────────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("platform:profile")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Account created. Build your player card next.")
            return redirect("platform:profile")
    else:
        form = SignUpForm()
    return render(request, "tournament/signup.html", {"form": form})


# ── Player Profile ───────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    profile = _get_or_create_profile(request.user)
    if request.method == "POST":
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved.")
            return redirect("platform:profile")
    else:
        form = PlayerProfileForm(instance=profile)
    return render(request, "tournament/profile.html", {"form": form, "profile": profile})


# ── Teams ────────────────────────────────────────────────────────────────────

def team_list_view(request):
    teams = Team.objects.prefetch_related("roster_profiles", "roster_profiles__user").order_by("name")
    return render(request, "tournament/team_list.html", {"teams": teams})


def team_detail_platform_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    profile = _get_or_create_profile(request.user) if request.user.is_authenticated else None
    is_captain = _is_captain(request.user, team)
    applications = team.applications.filter(status=APPLICATION_PENDING) if is_captain else None
    pending_invites = team.invites.filter(status=INVITE_PENDING) if is_captain else None
    can_apply = (
        request.user.is_authenticated
        and profile
        and profile.team_id != team.id
        and not team.applications.filter(profile=profile, status=APPLICATION_PENDING).exists()
    )
    context = {
        "team": team,
        "profile": profile,
        "is_captain": is_captain,
        "applications": applications,
        "pending_invites": pending_invites,
        "can_apply": can_apply,
        "application_form": TeamApplicationForm(),
    }
    return render(request, "tournament/team_detail_platform.html", context)


@login_required
def team_create_view(request):
    profile = _get_or_create_profile(request.user)
    if profile.team_id:
        messages.info(request, "Leave your current team before creating a new one.")
        return redirect("platform:team_detail", team_id=profile.team_id)
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.captain_user = request.user
            team.cap_email = request.user.email
            team.cap_name = request.user.first_name or request.user.username
            team.cap_surname = request.user.last_name or ""
            team.save()
            profile.team = team
            profile.save(update_fields=["team"])
            messages.success(request, f"{team.name} created. You are the captain.")
            return redirect("platform:team_detail", team_id=team.id)
    else:
        form = TeamCreateForm()
    return render(request, "tournament/team_create.html", {"form": form})


@login_required
@require_POST
def team_apply_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    profile = _get_or_create_profile(request.user)
    if profile.team_id == team.id:
        messages.info(request, "You are already on this team.")
        return redirect("platform:team_detail", team_id=team.id)
    if team.applications.filter(profile=profile).exclude(status=APPLICATION_REJECTED).exists():
        messages.info(request, "Application already pending.")
        return redirect("platform:team_detail", team_id=team.id)
    form = TeamApplicationForm(request.POST)
    if form.is_valid():
        application = form.save(commit=False)
        application.profile = profile
        application.team = team
        application.save()
        messages.success(request, "Application sent to the captain.")
    else:
        messages.error(request, "Could not send application.")
    return redirect("platform:team_detail", team_id=team.id)


@login_required
@require_POST
def team_application_resolve_view(request, application_id, action):
    application = get_object_or_404(TeamApplication, pk=application_id)
    if not _is_captain(request.user, application.team):
        return HttpResponseForbidden("Only the captain can manage applications.")
    profile = application.profile
    if action == "accept":
        application.status = APPLICATION_ACCEPTED
        application.resolved_at = timezone.now()
        profile.team = application.team
        profile.is_free_agent = False
        profile.save(update_fields=["team", "is_free_agent"])
        TeamApplication.objects.filter(
            profile=profile, status=APPLICATION_PENDING
        ).exclude(pk=application.pk).update(status=APPLICATION_REJECTED, resolved_at=timezone.now())
        application.save()
        messages.success(request, f"{profile} joined the team.")
    elif action == "reject":
        application.status = APPLICATION_REJECTED
        application.resolved_at = timezone.now()
        application.save()
        messages.success(request, "Application rejected.")
    else:
        messages.error(request, "Unknown action.")
    return redirect("platform:team_detail", team_id=application.team.id)


# ── Free Agent Board ─────────────────────────────────────────────────────────

def free_agent_board_view(request):
    position = request.GET.get("position", "")
    qs = PlayerProfile.objects.filter(is_free_agent=True, team__isnull=True).select_related("user")
    if position:
        qs = qs.filter(position=position)
    profiles = qs.order_by("-updated_at")
    captain_team = None
    if request.user.is_authenticated:
        captain_team = Team.objects.filter(captain_user=request.user).first()
    context = {
        "profiles": profiles,
        "position_choices": POSITION_CHOICES,
        "selected_position": position,
        "captain_team": captain_team,
    }
    return render(request, "tournament/free_agents.html", context)


@login_required
@require_POST
def send_invite_view(request, profile_id):
    profile = get_object_or_404(PlayerProfile, pk=profile_id)
    team = Team.objects.filter(captain_user=request.user).first()
    if not team:
        return HttpResponseForbidden("Only captains can send invites.")
    if profile.team_id:
        messages.error(request, "That player is already on a team.")
        return redirect("platform:free_agents")
    if team.invites.filter(profile=profile).exclude(status__in=[INVITE_REJECTED]).exists():
        messages.info(request, "Invite already sent.")
        return redirect("platform:free_agents")
    form = TeamInviteForm(request.POST)
    if form.is_valid():
        invite = form.save(commit=False)
        invite.team = team
        invite.profile = profile
        invite.save()
        messages.success(request, f"Invite sent to {profile}.")
    else:
        messages.error(request, "Could not send invite.")
    return redirect("platform:free_agents")


@login_required
@require_POST
def resolve_invite_view(request, invite_id, action):
    invite = get_object_or_404(TeamInvite, pk=invite_id, profile__user=request.user)
    if action == "accept":
        invite.status = INVITE_ACCEPTED
        invite.resolved_at = timezone.now()
        profile = invite.profile
        profile.team = invite.team
        profile.is_free_agent = False
        profile.save(update_fields=["team", "is_free_agent"])
        invite.save()
        messages.success(request, f"You joined {invite.team.name}.")
    elif action == "reject":
        invite.status = INVITE_REJECTED
        invite.resolved_at = timezone.now()
        invite.save()
        messages.info(request, "Invite declined.")
    else:
        messages.error(request, "Unknown action.")
    return redirect("platform:profile")



@login_required
@require_POST
def leave_team_view(request):
    profile = _get_or_create_profile(request.user)
    if not profile.team_id:
        return redirect("platform:profile")
    team = profile.team
    if team.captain_user_id == request.user.id:
        messages.error(request, "Transfer captaincy before leaving your team.")
        return redirect("platform:team_detail", team_id=team.id)
    profile.team = None
    profile.save(update_fields=["team"])
    messages.success(request, f"You left {team.name}.")
    return redirect("platform:profile")


# ── Player Card ──────────────────────────────────────────────────────────────

def player_card_view(request, profile_id=None):
    if profile_id:
        profile = get_object_or_404(PlayerProfile, pk=profile_id)
    elif request.user.is_authenticated:
        profile = _get_or_create_profile(request.user)
    else:
        return redirect("login")
    team = profile.team
    logo_url = None
    if team and team.logo_path:
        from django.conf import settings
        logo_url = f"{settings.MEDIA_URL.rstrip('/')}/{team.logo_path.lstrip('/')}"
    context = {
        "profile": profile,
        "team": team,
        "team_logo_url": logo_url,
        "position_label": profile.get_position_display() if profile.position else "UTILITY",
    }
    return render(request, "tournament/player_card.html", context)


# ── Pizzeria Kultowa Orders ──────────────────────────────────────────────────

@login_required
def pizza_order_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if not _is_captain(request.user, team):
        return HttpResponseForbidden("Only the captain can order pizzas.")
    orders = team.pizza_orders.select_related("created_by").order_by("-created_at")
    if request.method == "POST":
        form = PizzaOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.team = team
            order.created_by = request.user
            order.save()
            messages.success(request, f"{order.quantity}x {order.pizza_type} added.")
            return redirect("platform:pizza_order", team_id=team.id)
    else:
        form = PizzaOrderForm()
    summary = (
        PizzaOrder.objects.filter(team=team)
        .values("pizza_type")
        .annotate(total=Sum("quantity"))
        .order_by("pizza_type")
    )
    context = {
        "team": team,
        "form": form,
        "orders": orders,
        "summary": summary,
        "sponsor": PIZZERIA_KULTOWA,
    }
    return render(request, "tournament/pizza_order.html", context)


@login_required
@require_POST
def pizza_order_delete_view(request, order_id):
    order = get_object_or_404(PizzaOrder, pk=order_id)
    if not _is_captain(request.user, order.team):
        return HttpResponseForbidden("Only the captain can edit the pizza order.")
    order.delete()
    messages.success(request, "Pizza order removed.")
    return redirect("platform:pizza_order", team_id=order.team.id)


# ── Admin / Sponsor Summary (Control Room addition) ──────────────────────────

from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required(login_url="/panel/login/")
def pizza_admin_summary_view(request):
    orders = (
        PizzaOrder.objects.select_related("team")
        .values("pizza_type", "team__name")
        .annotate(total=Sum("quantity"))
        .order_by("pizza_type", "team__name")
    )
    type_totals = (
        PizzaOrder.objects.values("pizza_type")
        .annotate(total=Sum("quantity"))
        .order_by("pizza_type")
    )
    context = {
        "page_title": "Pizza Order Summary",
        "nav_section": "dashboard",
        "orders": orders,
        "type_totals": type_totals,
        "sponsor": PIZZERIA_KULTOWA,
        "pizza_choices": PIZZA_CHOICES,
    }
    return render(request, "panel/pizza_summary.html", context)

