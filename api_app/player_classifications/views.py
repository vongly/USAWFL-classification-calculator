from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import permissions
from .permissions import IsStaffUser

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

# UserModel
class UserViewSet(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'id'
    permission_classes = [IsStaffUser]

# Tournaments

class TournamentList(ListAPIView):

    serializer_class = serializers.TournamentSerializer
    queryset = models.Tournament.objects.all()

class TournamentRecord(RetrieveAPIView):

    serializer_class = serializers.TournamentSerializer
    queryset = models.Tournament.objects.all()
    lookup_field = 'slug'

class TournamentCreate(CreateAPIView):

    serializer_class = serializers.TournamentSerializer
    queryset = models.Tournament.objects.all()
    permission_classes = [IsStaffUser]

# Teams

class TeamList(ListAPIView):

    serializer_class = serializers.TeamSerializer
    
    def get_queryset(self):

        tournament_slug = self.request.query_params.get('tournament', None)
        if tournament_slug:
            all_players_in_tournament = models.TournamentPlayer.objects.all().filter(Tournament__slug=tournament_slug)
            teams_in_tournament = list(all_players_in_tournament.values('Player__Team').distinct())

            teams_in_tournament_list = [ item['Player__Team'] for item in teams_in_tournament]

            queryset = models.Team.objects.all().filter(ID__in=teams_in_tournament_list).order_by('TeamName')
        else:
            queryset = models.Team.objects.all()
        
        return queryset

class TeamRecord(RetrieveAPIView):

    serializer_class = serializers.TeamSerializer
    queryset = models.Team.objects.all()
    lookup_field = 'slug'    

class TeamCreate(CreateAPIView):

    serializer_class = serializers.TeamSerializer
    queryset = models.Team.objects.all()
    permission_classes = [IsStaffUser]

# Players

class PlayerList(ListAPIView):

    serializer_class = serializers.PlayerSerializer
    queryset = models.Player.objects.all()


class PlayerCreate(CreateAPIView):
    permission_classes = [IsStaffUser]

    serializer_class = serializers.PlayerCreateSerializer
    queryset = models.Player.objects.all()

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


# TournamentPlayers

class TournamentPlayerList(ListAPIView):

    serializer_class = serializers.TournamentPlayerSerializer

    def get_queryset(self):

        team_slug = self.request.query_params.get('team', None)
        tournament_slug = self.request.query_params.get('tournament', None)

        if tournament_slug and team_slug:
            queryset = models.TournamentPlayer.objects.all().filter(Tournament__slug=tournament_slug, Player__Team__slug=team_slug).order_by('PlayerNumber')
        elif tournament_slug:
            queryset = models.TournamentPlayer.objects.all().filter(Tournament__slug=tournament_slug).order_by('Player__Team__TeamName','PlayerNumber')
        else:
            queryset = models.TournamentPlayer.objects.all().order_by('-Tournament__Year','-Tournament__TournamentNumber','Player__Team__TeamName','PlayerNumber')
        
        return queryset

class TournamentPlayerFilter(ListAPIView):

    serializer_class = serializers.TournamentPlayerSerializer

    def filter_queryset(self, request, queryset, view):

        ids = request.query_params.get('id', None)

        if ids:
            ids = ids.split(',')
            ids = [int(id) for id in ids]

            queryset = models.TournamentPlayer.objects.all().filter(id__in=ids)
        else:
            queryset = models.TournamentPlayer.objects.all().order_by('-Tournament__Year','-Tournament__TournamentNumber','Player__Team__TeamName','PlayerNumber')
        
        return queryset

class TournamentPlayerCreateUpdate(APIView):
    permission_classes = [IsStaffUser]

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