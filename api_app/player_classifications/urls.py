
from django.urls import path

from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    #   Token Refresh
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #   User Model
    path('user/<int:id>', views.UserViewSet.as_view()),

    #   Tournaments
    path('tournaments/', views.TournamentList.as_view()),
    path('tournaments/<slug:slug>/', views.TournamentRecord.as_view()),

    #   Teams
    path('teams/', views.TeamList.as_view()),
    path('teams/<slug:slug>/', views.TeamRecord.as_view()),

    #   Players
    path('players/', views.PlayerList.as_view()),

    #   TournamentPlayers
    path('tournament_players/', views.TournamentPlayerList.as_view()),

    #   TournamentPlayers - specific upload/update view
    path('create_update/tournament_players/', views.TournamentPlayerCreateUpdate.as_view()),

    #   Stats
    path('stats/', views.StatList.as_view()),

    #   PlayerStats
    path('player_stats/', views.PlayerStatList.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)