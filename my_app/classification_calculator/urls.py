from django.urls import path

from .views import (
    auth_views,
    main_views,
    upload_views,
    stats_views,
)

urlpatterns = [
	path('refresh/', auth_views.refresh_token),

	path('login/', auth_views.login),
	path('logout/', auth_views.logout),

	path('upload/', upload_views.upload_update),
	path('upload/success/', upload_views.upload_update_success),
	path('upload/template/', upload_views.download_upload_template),

	path('stats/', stats_views.stats),

	path('', main_views.home),
	path('tournament/', main_views.tournament_list),
	path('tournament/<slug:tournament_slug>/', main_views.tournament_teams),
	path('tournament/<slug:tournament_slug>/<slug:team_slug>/', main_views.tournament_team_players),
]