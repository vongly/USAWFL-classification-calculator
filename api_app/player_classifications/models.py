from django.db import models

class Tournament(models.Model):
	id = models.AutoField(primary_key=True)
	number = models.IntegerField()
	year = models.IntegerField()
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=2)
	date = models.DateField()
	slug = models.SlugField(unique=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{} - {} - {}'.format(
			self.number.__str__(),
			self.year.__str__(),
			self.city.__str__()
		)

	class Meta:
		ordering = ['-year','-number']
		indexes = [
            models.Index(fields=['slug'], name='ix_tournament__slug'),
        ]

class Team(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=2)
	slug = models.SlugField(unique=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{} {}'.format(self.city.__str__(), self.name.__str__())

	class Meta:
		ordering = ['city', 'name',]
		indexes = [
            models.Index(fields=['slug'], name='ix_team__slug'),
        ]

class Player(models.Model):
	id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{}, {} - {} {}'.format(
			self.last_name.__str__(),
			self.first_name.__str__(),
			self.team.city.__str__(),
			self.team.name.__str__(),
		)

	class Meta:
		ordering = [
			'team__city',
			'team__name',
			'last_name',
			'first_name',
		]
		indexes = [
            models.Index(fields=['team_id'], name='ix_players__team_id'),
        ]

class Veteran(models.Model):
	id = models.AutoField(primary_key=True)
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{}, {} - {} {}'.format(
			self.player.last_name.__str__(),
			self.player.first_name.__str__(),
			self.player.team.city.__str__(),
			self.player.team.name.__str__(),
		)

	class Meta:
		ordering = [
			'player__team__city',
			'player__team__name',
			'player__last_name',
			'player__first_name',
		]

class TournamentPlayer(models.Model):
	id = models.AutoField(primary_key=True)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	player_number = models.IntegerField()
	classification_value = models.IntegerField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{}: {} #{} ({})'.format(
			self.tournament.__str__(),
			self.player.__str__(),
			self.player_number.__str__(),
			self.classification_value.__str__(),
		)

	class Meta:
		ordering = [
			'-tournament__year',
			'tournament__number',
			'player__team__city',
			'player__team__name',
			'player__last_name',
			'player__first_name',
		]
		indexes = [
            models.Index(fields=['tournament_id','player_id'], name='ix_tp__tid_pid'),
        ]

class Stat(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	value = models.IntegerField()
	slug = models.SlugField(unique=True)
	is_active = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ['name']

class PlayerStat(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)
	tournament_player = models.ForeignKey(TournamentPlayer, on_delete=models.CASCADE)
	stat = models.ForeignKey(Stat, on_delete=models.CASCADE)
	opponent = models.ForeignKey(Team, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{} {} - {} {} - {}: #{} {}, {} vs {} {}'.format(
			self.tournament_player.tournament.city.__str__(),
			self.tournament_player.tournament.year.__str__(),
			self.tournament_player.player.team.city.__str__(),
			self.tournament_player.player.team.name.__str__(),
			self.stat.name.__str__(),
			self.tournament_player.player_number.__str__(),
			self.tournament_player.player.last_name.__str__(),
			self.tournament_player.player.first_name.__str__(),
			self.opponent.city.__str__(),
			self.opponent.name.__str__(),
		)

	class Meta:
		ordering = [
			'-tournament_player__tournament__year',
			'tournament_player__tournament__city',
			'tournament_player__player__team__city',
			'tournament_player__player__team__name',
			'stat__name',
			'tournament_player__player_number',
		]