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
        'tournament_year': 'float64',
        'player_first_name': 'object',
        'player_last_name': 'object',
        'player_team_city': 'object',
        'player_team_name': 'object',
        'player_number': 'float64',
        'player_classification_value': 'float64',
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


    def check_expected_columns(self):
        missing_expected_column = [column for column in self.expected_columns if column not in self.uploaded_columns]

        if len(missing_expected_column) > 0:
            upload_error_message = f'You are missing one or more of the expected column(s). Expected columns are: { ", ".join(self.expected_columns) }.'
        else:
            upload_error_message = None

        return upload_error_message

    def check_all_fields_correct_dtype(self):
        # Check that all fields have the correct dtype
        wrong_dtype = []

        for column, expected_dtype in self.dtype_expected.items():
            actual_dtype = self.df[column].dtype
            if actual_dtype != expected_dtype:
                print(column, actual_dtype, expected_dtype)
                wrong_dtype.append(column)

        if len(wrong_dtype) > 0:
            upload_error_message = 'One or more fields are not in the correct format. Please make sure that all integer fields contain only integers.'
        else:
            upload_error_message = None

        return upload_error_message

    def check_for_blank_cells(self):
        blank_field = self.df.isna().any().any()
        if blank_field:
            upload_error_message = f'One or more cell(s) are empty. Make sure that there are no empty cells.'
        else:
            upload_error_message = None

        return upload_error_message

    def check_if_tournaments_exists(self):
        # Check that all uploaded tournaments exists (City Year)
        tournaments_that_dont_exist = [ t for t in self.tournament_city_year_uploaded if t not in self.tournament_city_year_existing ]
        if len(tournaments_that_dont_exist) > 0:
            upload_error_message = f'The following tournaments do not exist: { ", ".join(tournaments_that_dont_exist).title() }. Make sure that all uploaded tournament cities and corresponding years exist. '
        else:
            upload_error_message = None

        return upload_error_message

    def add_tournament_id_to_df(self):
        tournament_id_lookup = { f'{ t["city"].lower() } { t["year"] }': t['id'] for t in self.tournaments }
        self.df['tournament_id'] = self.df['tournament_city_year_combo'].map(tournament_id_lookup)

    def create_tournament_slugs_list(self):
        tournament_slug_lookup = { f'{ t["city"].lower() } { t["year"] }': t['slug'] for t in self.tournaments }
        tournament_slugs = self.df['tournament_city_year_combo'].map(tournament_slug_lookup).to_list()
        return tournament_slugs

    def check_if_teams_exists(self):
        # Check that all uploaded teams exists (City TeamName)
        self.df['team_city_name_combo'] = ( self.df['player_team_city'].apply(lambda x: x.lower()) + ' ' + self.df['player_team_name'].apply(lambda x: x.lower()) )
        teams_that_dont_exist = [ t for t in self.team_city_name_uploaded if t not in self.team_city_name_existing ]
        if len(teams_that_dont_exist) > 0:
            upload_error_message = f'The following tournaments do not exist: { ", ".join(teams_that_dont_exist).title() }. Make sure that all uploaded team cities and corresponding teams exist. '
        else:
            upload_error_message = None

        return upload_error_message

    def add_team_id_to_df(self):
        team_id_lookup = { f'{ t["city"].lower() } { t["name"].lower() }': t['id'] for t in self.teams }
        self.df['team_id'] = self.df['team_city_name_combo'].map(team_id_lookup)

    def create_team_slugs_list(self):
        team_slug_lookup = { f'{ t["city"].lower() } { t["name"].lower() }': t['slug'] for t in self.teams }
        team_slugs = self.df['team_city_name_combo'].map(team_slug_lookup).to_list()
        return team_slugs

    def check_class_values_between_1_to_5(self):
        # Check that all classification values are between 1-5
        classification_values_uploaded = self.df['player_classification_value'].apply(lambda x: int(x)).unique().tolist()
        classification_values_improper = [ value for value in classification_values_uploaded if value <= 0 or value > 5  ]

        if len(classification_values_improper) > 0:
            upload_error_message = 'All classification_values must be between 1-5, please enter proper classification values.'
        else:
            upload_error_message = None

        return upload_error_message

    def check_player_num_between_0_99(self):
        # Check that all player numbers are between 0-99
        player_numbers_uploaded = self.df['player_number'].apply(lambda x: int(x)).unique().tolist()
        player_numbers_improper = [ value for value in player_numbers_uploaded if value < 0 or value >= 100  ]

        if len(player_numbers_improper) > 0:
            upload_error_message = 'All player_number must be between 0-99, please enter proper player numbers.'
        else:
            upload_error_message = None

        return upload_error_message

    def convert_dtype(self):
        self.df = self.df.astype(self.dtype_map)

