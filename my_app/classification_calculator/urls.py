from django.urls import path

from . import views, views_admin_tools

urlpatterns = [
	path('refresh/', views_admin_tools.refresh_token),

	path('login/', views_admin_tools.login),
	path('logout/', views_admin_tools.logout),

	path('upload/', views_admin_tools.upload_update),
	path('upload/success/', views_admin_tools.upload_update_success),
	path('upload/template/', views_admin_tools.download_upload_template),


	path('', views.TournamentList),
	path('t/<slug:tournament_slug>/', views.TournamentTeams),
	path('t/<slug:tournament_slug>/<slug:team_slug>/', views.TournamentTeamPlayers),
]