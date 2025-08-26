from django.db import migrations

IX_TEAM_SLUG = 'ix_team_slug'
IX_TOURNAMENT_SLUG = 'ix_tournament_slug'
IX_PLAYERS_TEAM_ID = 'ix_players_team_id'
IX_TOURNAMENT_PLAYER_PID = 'ix_tournamentplayer_player_id'
IX_TOURNAMENT_PLAYER_TID_PID = 'ix_tournamentplayer_tournament_id_player_id'

def up(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return

    Team = apps.get_model('player_classifications', 'Team')
    Tournament = apps.get_model('player_classifications', 'Tournament')
    Player = apps.get_model('player_classifications', 'Player')
    TournamentPlayer = apps.get_model('player_classifications', 'TournamentPlayer')

    team_table = schema_editor.quote_name(Team._meta.db_table)
    tournament_table = schema_editor.quote_name(Tournament._meta.db_table)
    player_table = schema_editor.quote_name(Player._meta.db_table)
    tournament_player_table = schema_editor.quote_name(TournamentPlayer._meta.db_table)

    with schema_editor.connection.cursor() as c:
        # team -> team_slug
        c.execute(f'''
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS {IX_TEAM_SLUG}
            ON {team_table} (slug);
        ''')
        # tournament -> tournament_slug
        c.execute(f'''
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS {IX_TOURNAMENT_SLUG}
            ON {tournament_table} (slug);
        ''')
        # players -> team_id
        c.execute(f'''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS {IX_PLAYERS_TEAM_ID}
            ON {player_table} (team_id);
        ''')
        # tournament_players -> player_id
        c.execute(f'''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS {IX_TOURNAMENT_PLAYER_PID}
            ON {tournament_player_table} (player_id);
        ''')
        # composite to combine tournament filter + join key
        c.execute(f'''
            CREATE INDEX CONCURRENTLY IF NOT EXISTS {IX_TOURNAMENT_PLAYER_TID_PID}
            ON {tournament_player_table} (tournament_id, player_id);
        ''')

def down(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as c:
        c.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {IX_TEAM_SLUG};')
        c.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {IX_TOURNAMENT_SLUG};')
        c.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {IX_PLAYERS_TEAM_ID};')
        c.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {IX_TOURNAMENT_PLAYER_TID_PID};')
        c.execute(f'DROP INDEX CONCURRENTLY IF EXISTS {IX_TOURNAMENT_PLAYER_PID};')

class Migration(migrations.Migration):
    atomic = False  # REQUIRED for CONCURRENTLY

    dependencies = [
        ('player_classifications', '0011_veteran'),
    ]

    operations = [
        migrations.RunPython(up, down),
        # Optional: add state_operations with AddIndex(...) if you also declare these in models
        # via migrations.SeparateDatabaseAndState(...)
    ]