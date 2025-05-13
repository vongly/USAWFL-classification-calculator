from django.contrib import admin
from . import models

admin.site.register(models.Tournament)
admin.site.register(models.Team)
admin.site.register(models.Player)
admin.site.register(models.TournamentPlayer)
admin.site.register(models.Stat)
admin.site.register(models.PlayerStat)
