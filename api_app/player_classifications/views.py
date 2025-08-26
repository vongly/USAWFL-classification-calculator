from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import permissions
from .permissions import IsStaffUser, IsUser, CreateOnlyAuthenticated

from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)

from django.db.models import Q

from . import models
from . import serializers

from rest_framework_simplejwt.views import TokenObtainPairView

# Token Refresh
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.MyTokenObtainPairSerializer

# Django UserModel
class UserViewSet(RetrieveAPIView):
        
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'id'

# Tournaments

class TournamentList(ListCreateAPIView):
    serializer_class = serializers.TournamentSerializer
    queryset = models.Tournament.objects.all()

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

class TournamentRecord(RetrieveAPIView):
    serializer_class = serializers.TournamentSerializer
    queryset = models.Tournament.objects.all()
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

# Teams

# FILTERS: tournament=tournament_slug, team=team_slug (list accepted),
class TeamList(ListCreateAPIView):
    serializer_class = serializers.TeamSerializer
    
    def get_queryset(self):

        tournament_slug = self.request.query_params.get('tournament', None)

        if tournament_slug:
            all_players_in_tournament = models.TournamentPlayer.objects.filter(tournament__slug=tournament_slug)
            teams_in_tournament = list(all_players_in_tournament.values('player__team').distinct())
            teams_in_tournament_list = [ item['player__team'] for item in teams_in_tournament]

            queryset = models.Team.objects.filter(id__in=teams_in_tournament_list).order_by('name')
        else:
            queryset = models.Team.objects.all()
        
        return queryset

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

class TeamRecord(RetrieveAPIView):
    serializer_class = serializers.TeamSerializer
    queryset = models.Team.objects.all()
    lookup_field = 'slug'    

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

# Players

# FILTERS: team=team_slug, pid=player_id
class PlayerList(ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = serializers.PlayerSerializer
            return serializer_class
        serializer_class = serializers.PlayerCreateSerializer
        return serializer_class

    def get_queryset(self):
        team_slugs = self.request.query_params.getlist('team', None)
        player_ids = self.request.query_params.getlist('pid', None)

        if team_slugs and player_ids:
            try:
                player_ids = [ int(player_id) for player_id in player_ids ]
                queryset = models.Player.objects.filter(Team__slug__in=team_slugs, id__in=player_ids)
            except:
                queryset = models.Player.objects.filter(Team__slug__in=team_slugs)
        elif team_slugs:
            queryset = models.Player.objects.filter(Team__slug__in=team_slugs)
        elif player_ids:
            try:
                player_ids = [ int(player_id) for player_id in player_ids ]
                queryset = models.Player.objects.filter(id__in=player_ids)
            except:
                pass
        else:
            queryset = models.Player.objects.all()
        
        queryset = queryset.order_by('team__name', 'last_name', 'first_name')

        return queryset


    def create(self, request, *args, **kwargs):
        
        is_many = isinstance(request.data, list)

        if is_many and len(request.data) == 0:
            return Response([], status=status.HTTP_201_CREATED)
        
        else:
            serializer = self.get_serializer(data=request.data, many=is_many)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

class VeteranList(ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = serializers.VeteranSerializer
            return serializer_class
        serializer_class = serializers.VeteranCreateSerializer
        return serializer_class

    def get_queryset(self):
        team_slugs = self.request.query_params.getlist('team', None)
        player_ids = self.request.query_params.getlist('pid', None)

        if team_slugs and player_ids:
            try:
                player_ids = [ int(player_id) for player_id in player_ids ]
                queryset = models.Veteran.objects.filter(Player__Team__slug__in=team_slugs, Player__id__in=player_ids)
            except:
                queryset = models.Veteran.objects.filter(Player__Team__slug__in=team_slugs)
        elif team_slugs:
            queryset = models.Veteran.objects.filter(Player__Team__slug__in=team_slugs)
        elif player_ids:
            try:
                player_ids = [ int(player_id) for player_id in player_ids ]
                queryset = models.Veteran.objects.filter(Player__id__in=player_ids)
            except:
                pass
        else:
            queryset = models.Veteran.objects.all()
        
        queryset = queryset.order_by('player__team__name', 'player__last_name', 'player__first_name')

        return queryset


    def create(self, request, *args, **kwargs):
        
        is_many = isinstance(request.data, list)

        if is_many and len(request.data) == 0:
            return Response([], status=status.HTTP_201_CREATED)
        
        else:
            serializer = self.get_serializer(data=request.data, many=is_many)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

# TournamentPlayers

# FILTERS: tpid=tournament_id (list accepted), pid=player_id (list accepted), team=team_slug (list accepted)
class TournamentPlayerList(ListAPIView):
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = serializers.TournamentPlayerSerializer
            return serializer_class
        serializer_class = serializers.TournamentPlayerCreateSerializer
        return serializer_class

    def get_queryset(self):

        tournament_player_ids = self.request.query_params.getlist('tpid', None)
        player_ids = self.request.query_params.getlist('pid', None)

        tournament_slugs = self.request.query_params.getlist('tournament', None)
        team_slugs = self.request.query_params.getlist('team', None)

        if tournament_player_ids:
            tournament_player_ids = [ int(tournament_player_id) for tournament_player_id in tournament_player_ids ]
            queryset = models.TournamentPlayer.objects.filter(id__in=tournament_player_ids)
        elif player_ids:
            player_ids = [ int(player_id) for player_id in player_ids ]
            queryset = models.TournamentPlayer.objects.filter(player__id__in=player_ids)
        elif tournament_slugs and team_slugs:
            queryset = models.TournamentPlayer.objects.filter(tournament__slug__in=tournament_slugs, player__team__slug__in=team_slugs)
        elif tournament_slugs:
            queryset = models.TournamentPlayer.objects.filter(tournament__slug__in=tournament_slugs)
        elif team_slugs:
            queryset = models.TournamentPlayer.objects.filter(player__team__slug__in=team_slugs)
        else:
            queryset = models.TournamentPlayer.objects.all()
        
        queryset = queryset.order_by('-tournament__year','-tournament__number','player__team__name','player_number')

        return queryset

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

class TournamentPlayerCreateUpdate(APIView):
    permission_classes = [IsStaffUser()]

    def post(self, request, *args, **kwargs):
        data = request.data

        created = []
        updated = []
        errors = []

        for item in data:
            obj = None
            if 'id' in item:
                try:
                    obj = models.TournamentPlayer.objects.get(id=item['id'])
                except models.TournamentPlayer.DoesNotExist:
                    obj = None

            if obj:
                serializer = serializers.TournamentPlayerCreateSerializer(obj, data=item, partial=True)
            else:
                serializer = serializers.TournamentPlayerCreateSerializer(data=item)

            if serializer.is_valid():
                instance = serializer.save()
                if obj:
                    updated.append(instance)
                else:
                    created.append(instance)
            else:
                errors.append(serializer.errors)

        result = {
            'created': serializers.TournamentPlayerCreateSerializer(created, many=True).data,
            'updated': serializers.TournamentPlayerCreateSerializer(updated, many=True).data,
            'errors': errors
        }

        return Response(result, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]

class StatList(ListCreateAPIView):
    serializer_class = serializers.StatSerializer

    def get_queryset(self):

        is_active = self.request.query_params.get('is_active', None)
        slug = self.request.query_params.get('slug', None)

        if is_active and is_active.lower() in ['true','false'] and slug:
            if is_active.lower() == 'true':
                is_active_value = True
            elif is_active.lower() == 'false':
                is_active_value = False
            queryset = models.Stat.objects.filter(is_active=is_active_value, slug=slug)
        elif slug:
            queryset = models.Stat.objects.filter(slug=slug)
        elif is_active and is_active.lower() in ['true','false']:
            if is_active.lower() == 'true':
                is_active_value = True
            elif is_active.lower() == 'false':
                is_active_value = False
            queryset = models.Stat.objects.filter(is_active=is_active_value)
        else:
            queryset = models.Stat.objects.all()
        
        queryset = queryset.order_by('name')

        return queryset
    
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []
        return [IsStaffUser()]


# FILTERS: tournament=tournament_slug, team=team_slug (list accepted), stat=stat_slug (list accepted)
class PlayerStatList(ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = serializers.PlayerStatSerializer
            return serializer_class
        serializer_class = serializers.PlayerStatCreateSerializer
        return serializer_class

    def get_queryset(self):


        tournaments = self.request.query_params.getlist('tournament', None)
        teams = self.request.query_params.getlist('team', None)
        stats = self.request.query_params.getlist('stat', None)

        if tournaments:
            tournaments = [ tournament for tournament in tournaments ]
        if teams:
            teams = [ team for team in teams ]
        if stats:
            stats = [ stat for stat in stats ]

        if tournaments and teams and stats:
            queryset = models.PlayerStat.objects.filter(
                tournament_player__tournament__slug__in=tournaments,
                tournament_player__player__team__slug__in=teams,
                stat__slug__in=stats,
            )
        elif tournaments and teams:
            queryset = models.PlayerStat.objects.filter(
                tournament_player__tournament__slug__in=tournaments,
                tournament_player__player__team__slug__in=teams,
            )
        elif tournaments and stats:
            queryset = models.PlayerStat.objects.filter(
                tournament_player__tournament__slug__in=tournaments,
                stat__slug__in=stats,
            )
        elif teams and stats:
            queryset = models.PlayerStat.objects.filter(
                tournament_player__tournament__slug__in=tournaments,
                tournament_player__player__team__slug__in=teams,
                stat__slug__in=stats,
            )
        elif tournaments:
            queryset = models.PlayerStat.objects.filter(
                tournament_player__tournament__slug__in=tournaments,
            )
        elif teams:
            queryset = models.PlayerStat.objects.filter(
                tournament_player__player__team__slug__in=teams,
            )
        elif stats:
            queryset = models.PlayerStat.objects.filter(
                stat__slug__in=stats,
            )
        else:
            queryset = models.PlayerStat.objects.all()

        return queryset

    def get_permissions(self):
        if self.request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']:
            return []
        return [IsUser()]