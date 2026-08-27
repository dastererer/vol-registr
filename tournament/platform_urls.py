from django.urls import path

from . import phase2_views, platform_views

app_name = "platform"

urlpatterns = [
    # Auth
    path("signup/", platform_views.signup_view, name="signup"),
    # Profile
    path("profile/", platform_views.profile_view, name="profile"),
    path("profile/card/", platform_views.player_card_view, name="my_card"),
    path("profile/card/<int:profile_id>/", platform_views.player_card_view, name="player_card"),
    path("profile/leave-team/", platform_views.leave_team_view, name="leave_team"),
    # Teams
    path("teams/", platform_views.team_list_view, name="team_list"),
    path("teams/create/", platform_views.team_create_view, name="team_create"),
    path("teams/<int:team_id>/", platform_views.team_detail_platform_view, name="team_detail"),
    path("teams/<int:team_id>/apply/", platform_views.team_apply_view, name="team_apply"),
    path(
        "teams/applications/<int:application_id>/<str:action>/",
        platform_views.team_application_resolve_view,
        name="application_resolve",
    ),
    # Free agents
    path("free-agents/", platform_views.free_agent_board_view, name="free_agents"),
    path(
        "free-agents/<int:profile_id>/invite/",
        platform_views.send_invite_view,
        name="send_invite",
    ),
    path(
        "invites/<int:invite_id>/<str:action>/",
        platform_views.resolve_invite_view,
        name="resolve_invite",
    ),
    # Pizza
    path("teams/<int:team_id>/pizza/", platform_views.pizza_order_view, name="pizza_order"),
    path("pizza/<int:order_id>/delete/", platform_views.pizza_order_delete_view, name="pizza_delete"),
    # Power Rankings
    path("rankings/", phase2_views.rankings_list_view, name="rankings"),
    path("rankings/<int:article_id>/", phase2_views.ranking_detail_view, name="ranking_detail"),
    path("rankings/create/", phase2_views.ranking_create_view, name="ranking_create"),
    # Live Feed
    path("live-feed/", phase2_views.live_feed_view, name="live_feed"),
    path("live-feed/submit/", phase2_views.highlight_submit_view, name="highlight_submit"),
]
