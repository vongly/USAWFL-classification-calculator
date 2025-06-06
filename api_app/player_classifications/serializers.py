from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from . import models

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_staff']

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tournament
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Team
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = models.Player
        fields = '__all__'

class PlayerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Player
        fields = '__all__'

class TournamentPlayerSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = models.TournamentPlayer
        fields = '__all__'

class TournamentPlayerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TournamentPlayer
        fields = '__all__'

class StatSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Stat
        fields = '__all__'

class PlayerStatSerializer(serializers.ModelSerializer):
    tournament_player = TournamentPlayerSerializer(read_only=True)
    stat = StatSerializer(read_only=True)
    opponent = TeamSerializer(read_only=True)

    class Meta:
        model = models.PlayerStat
        fields = '__all__'

class PlayerStatCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PlayerStat
        fields = '__all__'
