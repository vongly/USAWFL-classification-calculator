from django.db import models

class Tournament(models.Model):
	ID = models.AutoField(primary_key=True)
	TournamentNumber = models.IntegerField()
	Year = models.IntegerField()
	City = models.CharField(max_length=50)
	State = models.CharField(max_length=2)
	Date = models.DateField()
	slug = models.SlugField()

	def __str__(self):
		return '{} - {} - {}'.format(
			self.TournamentNumber.__str__(),
			self.Year.__str__(),
			self.City.__str__()
		)

	class Meta:
		ordering = ['-Year','TournamentNumber']

class Team(models.Model):
	ID = models.AutoField(primary_key=True)
	TeamName = models.CharField(max_length=50)
	City = models.CharField(max_length=50)
	State = models.CharField(max_length=2)
	slug = models.SlugField()

	def __str__(self):
		return '{} {}'.format(self.City.__str__(), self.TeamName.__str__())

	class Meta:
		ordering = ['City', 'TeamName',]


class Player(models.Model):
	ID = models.AutoField(primary_key=True)
	PlayerFirstName = models.CharField(max_length=50)
	PlayerLastName = models.CharField(max_length=50)
	Team = models.ForeignKey(Team, on_delete=models.CASCADE)

	def __str__(self):
		return '{}, {} - {} {}'.format(
			self.PlayerLastName.__str__(),
			self.PlayerFirstName.__str__(),
			self.Team.City.__str__(),
			self.Team.TeamName.__str__(),
		)

	class Meta:
		ordering = [
			'Team__City',
			'Team__TeamName',
			'PlayerLastName',
			'PlayerFirstName',
		]

class TournamentPlayer(models.Model):
	Tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	Player = models.ForeignKey(Player, on_delete=models.CASCADE)
	PlayerNumber = models.IntegerField()
	ClassificationValue = models.IntegerField()

	def __str__(self):
		return '{}: {} #{} ({})'.format(
			self.Tournament.__str__(),
			self.Player.__str__(),
			self.PlayerNumber.__str__(),
			self.ClassificationValue.__str__(),
		)

	class Meta:
		ordering = [
			'-Tournament__Year',
			'Tournament__TournamentNumber',
			'Player__Team__City',
			'Player__Team__TeamName',
			'Player__PlayerLastName',
			'Player__PlayerFirstName',
		]
