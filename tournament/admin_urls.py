from django.urls import path

from .panel.auth_views import panel_login, panel_logout
from .panel.checkin_views import checkin_search, checkin_toggle, checkin_view
from .panel.dashboard_views import dashboard_view

from .panel.team_views import (
    generate_roster_code,
    team_batch_action,
    team_create_view,
    team_delete_view,
    team_detail_view,
    team_drawer_view,
    team_edit_view,
    team_pipeline_move,
    team_status_action,
    teams_list_view,
    teams_pipeline_view,
)
from .panel.player_views import (
    player_create_view,
    player_delete_view,
    player_detail_view,
    player_edit_view,
    players_list_view,
)
from .panel.backup_views import (
    db_backup_create,
    db_backup_delete,
    db_backup_download,
    db_backup_view,
    db_download_current,
    db_restore,
)
app_name = "panel"

urlpatterns = [
    path("login/", panel_login, name="login"),
    path("logout/", panel_logout, name="logout"),
    path("", dashboard_view, name="dashboard"),
    path("teams/", teams_list_view, name="teams"),
    path("teams/pipeline/", teams_pipeline_view, name="teams_pipeline"),
    path("teams/create/", team_create_view, name="team_create"),
    path("teams/<int:pk>/", team_detail_view, name="team_detail"),
    path("teams/<int:pk>/edit/", team_edit_view, name="team_edit"),
    path("teams/<int:pk>/delete/", team_delete_view, name="team_delete"),
    path("teams/<int:pk>/status/", team_status_action, name="team_status"),
    path("teams/<int:pk>/roster-code/", generate_roster_code, name="generate_roster_code"),
    path("teams/<int:pk>/drawer/", team_drawer_view, name="team_drawer"),
    path("teams/<int:pk>/pipeline-move/", team_pipeline_move, name="team_pipeline_move"),
    path("teams/batch/", team_batch_action, name="team_batch"),
    path("checkin/", checkin_view, name="checkin"),
    path("checkin/search/", checkin_search, name="checkin_search"),
    path("checkin/<int:pk>/toggle/", checkin_toggle, name="checkin_toggle"),
    path("players/", players_list_view, name="players"),
    path("players/create/", player_create_view, name="player_create"),
    path("players/<int:pk>/", player_detail_view, name="player_detail"),
    path("players/<int:pk>/edit/", player_edit_view, name="player_edit"),
    path("players/<int:pk>/delete/", player_delete_view, name="player_delete"),
    # ── DB Backup / Restore ──
    path("backup/", db_backup_view, name="db_backup"),
    path("backup/create/", db_backup_create, name="db_backup_create"),
    path("backup/download/<str:filename>/", db_backup_download, name="db_backup_download"),
    path("backup/download-current/", db_download_current, name="db_download_current"),
    path("backup/restore/", db_restore, name="db_restore"),
    path("backup/<str:filename>/delete/", db_backup_delete, name="db_backup_delete"),
]
