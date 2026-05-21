from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.index),
    # ── Tournament section ──────────────────────────────
    path('tournament/team/<int:team_id>/', views.tournament_team, name='tournament_team'),
    # ── Other pages ─────────────────────────────────────
    path('register/', views.register, name='register'),
    path('faq/', views.faq, name='faq'),
    path('api/register/', views.api_register_team, name='api_register'),
    path('api/vote/', views.api_vote_team, name='api_vote_team'),
    path('vote/confirm/<uuid:token>/', views.vote_confirm, name='vote_confirm'),
    path('api/soundcloud-search/', views.api_soundcloud_search, name='api_soundcloud_search'),
    path('api/ask/', views.api_ask_question, name='api_ask_question'),
    path('roster/', views.roster_update_view, name='roster_update'),
    path('privacy-policy/', views.privacy_policy_en, name='privacy_policy_en'),
]
