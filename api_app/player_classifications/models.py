from django.db import models

class Tournament(models.Model):
	id = models.AutoField(primary_key=True)
	number = models.IntegerField()
	year = models.IntegerField()
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=2)
	date = models.DateField()
	slug = models.SlugField()

	def __str__(self):
		return '{} - {} - {}'.format(
			self.number.__str__(),
			self.year.__str__(),
			self.city.__str__()
		)

	class Meta:
		ordering = ['-year','-number']

class Team(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=2)
	slug = models.SlugField()

	def __str__(self):
		return '{} {}'.format(self.city.__str__(), self.name.__str__())

	class Meta:
		ordering = ['city', 'name',]


class Player(models.Model):
	id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)

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

class TournamentPlayer(models.Model):
	id = models.AutoField(primary_key=True)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	player_number = models.IntegerField()
	classification_value = models.IntegerField()

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
