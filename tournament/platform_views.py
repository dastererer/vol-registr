"""Lean public platform views without user accounts or duplicate team entities."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .constants import PAYMENT_REFUND
from .forms import FreeAgentApplicationForm
from .models import Team

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def free_agent_view(request):
    """Collect a no-account request and notify the selected team captain."""

    submitted = False
    delivery_deferred = False

    if request.method == "POST":
        form = FreeAgentApplicationForm(request.POST)
        # A visually hidden honeypot absorbs unsophisticated form bots.
        if request.POST.get("website", "").strip():
            return render(
                request,
                "tournament/free_agents.html",
                {"form": FreeAgentApplicationForm(), "submitted": True},
            )

        if form.is_valid():
            application = form.save()
            subject = (
                f"[Court Cup 3] {application.first_name} {application.last_name} "
                f"wants to join {application.team.name}"
            )
            body = "\n".join(
                [
                    f"Team: {application.team.name}",
                    f"Player: {application.first_name} {application.last_name}",
                    f"Email: {application.email}",
                    "",
                    "Message:",
                    application.message,
                    "",
                    "Reply directly to this email to contact the player.",
                ]
            )
            try:
                EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[application.team.cap_email],
                    reply_to=[application.email],
                ).send(fail_silently=False)
            except Exception:
                delivery_deferred = True
                logger.exception(
                    "Free-agent request %s saved, but captain email delivery failed",
                    application.pk,
                )
            else:
                application.email_sent = True
                application.save(update_fields=["email_sent"])

            submitted = True
            form = FreeAgentApplicationForm()
    else:
        selected_team = request.GET.get("team", "")
        form = FreeAgentApplicationForm(initial={"team": selected_team})

    return render(
        request,
        "tournament/free_agents.html",
        {
            "form": form,
            "submitted": submitted,
            "delivery_deferred": delivery_deferred,
            "registered_team_count": Team.objects.exclude(
                payment_status=PAYMENT_REFUND
            ).count(),
        },
    )


def legacy_home_redirect(request, *args, **kwargs):
    """Retire experimental public-platform pages without leaving dead links."""

    return redirect("index")


def legacy_profile_redirect(request, *args, **kwargs):
    """The code-protected team profile replaces public user accounts."""

    return redirect("roster_update")


def legacy_team_list_redirect(request, *args, **kwargs):
    """The homepage registered-teams modal is the only public team index."""

    return HttpResponseRedirect(f"{reverse('index')}#registeredTeamsModal")


def legacy_registration_redirect(request, *args, **kwargs):
    """Creating a team always means registering it for the tournament."""

    return redirect("register")


def legacy_team_redirect(request, team_id, *args, **kwargs):
    """Keep old shared team links pointing at the canonical tournament page."""

    team = get_object_or_404(Team, pk=team_id)
    return redirect("tournament_team", team_id=team.pk)
