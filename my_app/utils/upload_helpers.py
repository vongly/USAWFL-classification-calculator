

class AddUpdateTournamentPlayers:
    
    expected_columns = [
        'tournament_city',
        'tournament_year',
        'player_first_name',
        'player_last_name',
        'player_team_city',
        'player_team_name',
        'player_number',
        'player_classification_value',
    ]

    dtype_map = {
        'tournament_city': str,
        'tournament_year': int,
        'player_first_name': str,
        'player_last_name': str,
        'player_team_city': str,
        'player_team_name': str,
        'player_number': int,
        'player_classification_value': int,
    }

    dtype_expected = {
        'tournament_city': 'object',
        'tournament_year': 'int64',
        'player_first_name': 'object',
        'player_last_name': 'object',
        'player_team_city': 'object',
        'player_team_name': 'object',
        'player_number': 'int64',
        'player_classification_value': 'int64',
    }

    def __init__(self, df, tournaments, teams):
        self.df = df
        self.tournaments = tournaments
        self.teams = teams
        self.uploaded_columns = df.columns.to_list()

        self.df['tournament_city_year_combo'] = ( self.df['tournament_city'].apply(lambda x: x.lower()) + ' ' + self.df['tournament_year'].apply(lambda x: str(int(x))) )
        self.tournament_city_year_uploaded = df['tournament_city_year_combo'].unique().tolist()
        self.tournament_city_year_existing = [ f'{ t["city"].lower() } { t["year"] }' for t in tournaments ]

        self.df['team_city_name_combo'] = ( self.df['player_team_city'].apply(lambda x: x.lower()) + ' ' + self.df['player_team_name'].apply(lambda x: x.lower()) )
        self.team_city_name_uploaded = df['team_city_name_combo'].unique().tolist()
        self.team_city_name_existing = [ f'{ team["city"].lower() } { team["name"].lower() }' for team in teams ]


    # Validation functions
    def check_expected_columns(self):
        missing_expected_column = [column for column in self.expected_columns if column not in self.uploaded_columns]
        if missing_expected_column:
            return f'You are missing one or more of the expected column(s). Expected columns are: { ", ".join(self.expected_columns) }.'
        return None

    def check_all_fields_correct_dtype(self):
        # Check that all fields have the correct dtype
        wrong_dtype = []

        for column, expected_dtype in self.dtype_expected.items():
            actual_dtype = self.df[column].dtype
            if expected_dtype == 'int64':
                try:
                    self.df[column] = self.df[column].astype(int)
                except:
                    pass
            if actual_dtype != expected_dtype:
                wrong_dtype.append(column)

        if wrong_dtype:
            return 'One or more fields are not in the correct format. Please make sure that all integer fields contain only integers.'
        return None

    def check_for_blank_cells(self):
        blank_field = self.df.isna().any().any()
        if blank_field:
            return f'One or more cell(s) are empty. Make sure that there are no empty cells.'
        return None

    def check_if_tournaments_exists(self):
        # Check that all uploaded tournaments exists (City Year)
        tournaments_that_dont_exist = [ t for t in self.tournament_city_year_uploaded if t not in self.tournament_city_year_existing ]
        if tournaments_that_dont_exist:
            return f'The following tournaments do not exist: { ", ".join(tournaments_that_dont_exist).title() }. Make sure that all uploaded tournament cities and corresponding years exist. '
        return None

    def check_if_teams_exists(self):
        # Check that all uploaded teams exists (City TeamName)
        self.df['team_city_name_combo'] = ( self.df['player_team_city'].apply(lambda x: x.lower()) + ' ' + self.df['player_team_name'].apply(lambda x: x.lower()) )
        teams_that_dont_exist = [ t for t in self.team_city_name_uploaded if t not in self.team_city_name_existing ]
        if teams_that_dont_exist:
           return f'The following tournaments do not exist: { ", ".join(teams_that_dont_exist).title() }. Make sure that all uploaded team cities and corresponding teams exist. '
        return None

    def check_class_values_between_1_to_5(self):
        # Check that all classification values are between 1-5
        classification_values = self.df['player_classification_value'].apply(lambda x: int(x)).unique().tolist()
        if any(value <= 0 or value > 5 for value in classification_values):
            return 'All classification_values must be between 1-5, please enter proper classification values.'
        return None

    def check_player_num_between_0_99(self):
        # Check that all player numbers are between 0-99
        player_numbers = self.df['player_number'].apply(lambda x: int(x)).unique().tolist()
        if any(num < 0 or num >= 100 for num in player_numbers):
            return 'All player_number values must be between 0-99, please enter proper player numbers.'
        return None

    # Map ids
    def add_tournament_id_to_df(self):
        tournament_id_lookup = { f'{ t["city"].lower() } { t["year"] }': t['id'] for t in self.tournaments }
        self.df['tournament_id'] = self.df['tournament_city_year_combo'].map(tournament_id_lookup)

    def add_team_id_to_df(self):
        team_id_lookup = { f'{ t["city"].lower() } { t["name"].lower() }': t['id'] for t in self.teams }
        self.df['team_id'] = self.df['team_city_name_combo'].map(team_id_lookup)

    def convert_dtype(self):
        self.df = self.df.astype(self.dtype_map)

    # Map slugs
    def create_tournament_slugs_list(self):
        tournament_slug_lookup = { f'{ t["city"].lower() } { t["year"] }': t['slug'] for t in self.tournaments }
        tournament_slugs = self.df['tournament_city_year_combo'].map(tournament_slug_lookup).to_list()
        return tournament_slugs

    def create_team_slugs_list(self):
        team_slug_lookup = { f'{ t["city"].lower() } { t["name"].lower() }': t['slug'] for t in self.teams }
        team_slugs = self.df['team_city_name_combo'].map(team_slug_lookup).to_list()
        return team_slugs