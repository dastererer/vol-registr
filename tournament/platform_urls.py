"""Compatibility routes for the retired account/platform experiment."""

from django.urls import path

from . import platform_views

app_name = "platform"

urlpatterns = [
    path("free-agents/", platform_views.free_agent_view, name="free_agents"),
    path("profile/", platform_views.legacy_profile_redirect, name="profile"),
    path("profile/card/", platform_views.legacy_profile_redirect, name="my_card"),
    path(
        "profile/card/<int:profile_id>/",
        platform_views.legacy_profile_redirect,
        name="player_card",
    ),
    path("profile/leave-team/", platform_views.legacy_profile_redirect, name="leave_team"),
    path("signup/", platform_views.legacy_home_redirect, name="signup"),
    path("teams/", platform_views.legacy_team_list_redirect, name="team_list"),
    path("teams/create/", platform_views.legacy_registration_redirect, name="team_create"),
    path("teams/<int:team_id>/", platform_views.legacy_team_redirect, name="team_detail"),
    path(
        "teams/<int:team_id>/apply/",
        platform_views.legacy_team_redirect,
        name="team_apply",
    ),
    path(
        "teams/applications/<int:application_id>/<str:action>/",
        platform_views.legacy_home_redirect,
        name="application_resolve",
    ),
    path(
        "free-agents/<int:profile_id>/invite/",
        platform_views.legacy_home_redirect,
        name="send_invite",
    ),
    path(
        "invites/<int:invite_id>/<str:action>/",
        platform_views.legacy_home_redirect,
        name="resolve_invite",
    ),
    path("teams/<int:team_id>/pizza/", platform_views.legacy_team_redirect, name="pizza_order"),
    path("pizza/<int:order_id>/delete/", platform_views.legacy_home_redirect, name="pizza_delete"),
    path("rankings/", platform_views.legacy_home_redirect, name="rankings"),
    path(
        "rankings/<int:article_id>/",
        platform_views.legacy_home_redirect,
        name="ranking_detail",
    ),
    path("rankings/create/", platform_views.legacy_home_redirect, name="ranking_create"),
    path("live-feed/", platform_views.legacy_home_redirect, name="live_feed"),
    path("live-feed/submit/", platform_views.legacy_home_redirect, name="highlight_submit"),
]
