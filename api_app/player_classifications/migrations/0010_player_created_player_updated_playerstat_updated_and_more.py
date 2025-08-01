# Generated by Django 4.2.20 on 2025-07-31 17:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player_classifications', '0009_alter_stat_slug_alter_team_slug_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 31, 17, 34, 54, 870764)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='playerstat',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='stat',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 31, 17, 34, 56, 772755)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stat',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='team',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 31, 17, 34, 58, 443932)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 31, 17, 35, 0, 41167)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tournament',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='tournamentplayer',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 7, 31, 17, 35, 1, 567787)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tournamentplayer',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
