from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse

import json
import requests
import jwt
import csv

from env import api_base_url, token_name, API_KEY
import requests

import pandas as pd

admin_url = None

def refresh_token(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')

    previous_url = request.session['previous_url']

    try:
        url = f'{ api_base_url }/refresh/'
        call = requests.post(url=url, data={'refresh': request.COOKIES.get(f'{ token_name }_refresh')})
        tokens = call.json()

        response = HttpResponseRedirect(previous_url)

        response.set_cookie(
            f'{ token_name }_access',
            tokens['access'],
            httponly=True,
            samesite='Strict',
        )
        response.set_cookie(
            f'{ token_name }_refresh',
            tokens['refresh'],
            httponly=True,
            samesite='Strict',
        )

        return response

    except:
        if access_token:
            response = HttpResponseRedirect('/login/')
            response.delete_cookie(f'{ token_name }_access')
            response.delete_cookie(f'{ token_name }_refresh')

        return response

def login(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')
    admin_url = None

    if access_token:
        headers = {
            'Authorization': f'Bearer { access_token }'
        }
        try:
            jwt.decode(access_token, API_KEY, algorithms='HS256')
        except:
            request.session['previous_session'] = request.path
            HttpResponseRedirect('/refresh/')
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        url = f'{ api_base_url }/token/'
        form = request.POST

        data_validate_user = {
            'username': form.get('username'),
            'password': form.get('password'),
        }

        call_validate_user = requests.post(url=url, data=data_validate_user)

        if call_validate_user.status_code == 200:
            tokens = call_validate_user.json()
            response = HttpResponseRedirect('/')
            response.set_cookie(
                f'{ token_name }_access',
                tokens['access'],
                httponly=True,
                samesite='Strict',
            )
            response.set_cookie(
                f'{ token_name }_refresh',
                tokens['refresh'],
                httponly=True,
                samesite='Strict',
            )

            return response

        elif call_validate_user.status_code == 401:
            response = 'Incorrect username or password'
            return render(request, 'login.html', {
                    'admin_url': admin_url,
                    'request': request,
                    'response': response,
                }
            )
        else:
            response = call_validate_user.status_code
            return render(request, 'login.html', {
                    'admin_url': admin_url,
                    'request': request,
                    'response': response,
                }
            )

    return render(request, 'login.html',{
            'admin_url': admin_url,
        }
    )

def logout(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')
    if access_token:
        response = HttpResponseRedirect('/')
        response.delete_cookie(f'{ token_name }_access')
        response.delete_cookie(f'{ token_name }_refresh')
        return response
    return HttpResponseRedirect('/')


def upload_update(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')

    admin_url = None

    if access_token:
        headers = {
            'Authorization': f'Bearer { access_token }'
        }
        try:
            payload = jwt.decode(access_token, API_KEY, algorithms='HS256')
            user_id = payload.get('user_id')
            user = requests.get(url=f'{ api_base_url }/user/{ user_id }', headers=headers).json()
            
            if user['is_staff']:
                admin_url = f'{ api_base_url }/admin'
        except:
            request.session['previous_url'] = request.path
            return HttpResponseRedirect('/refresh/')

    elif not access_token:
        return HttpResponseRedirect('/')

    try:
        del request.session['template_headers']
    except:
        pass

    try:
        del request.session['results_created_players']
    except:
        pass

    try:
        del request.session['results_created_update_tournament_players']
    except:
        pass

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

    request.session['template_headers'] = expected_columns

    url_tournaments = f'{ api_base_url }/tournaments/'
    call_tournaments = requests.get(url=url_tournaments)
    tournaments = call_tournaments.json()

    url_teams = f'{ api_base_url }/teams/'
    call_teams = requests.get(url=url_teams)
    teams = call_teams.json()

    url_tournament_players = f'{ api_base_url }/tournament_players/'
    call_tournament_players = requests.get(url=url_tournament_players)
    tournament_players = call_tournament_players.json()

    if request.method == 'POST':
        upload_file = request.FILES.get('upload_file')


        # Dataframe
        df = pd.read_csv(upload_file)
        # Clean Dataframe
        df = df.dropna(how='all')
        for column in df.columns:
            df[column.strip().lower()] = df[column].map(lambda x: x.strip() if isinstance(x, str) else x)

        uploaded_columns = df.columns.to_list()

        ### Data Validation Checks ###

        # Tests
        upload_error_message = None

        # Check for missing expected columns
        try:
            missing_expected_column = [column for column in expected_columns if column not in uploaded_columns]
            if len(missing_expected_column) > 0:
                upload_error_message = f'You are missing one or more of the expected column(s). Expected columns are: { ", ".join(expected_columns) }.'
        except:
            pass

        # Check for blank cells in upload file
        try:
            blank_field = df.isna().any().any()
            if blank_field:
                upload_error_message = f'One or more cell(s) are empty. Make sure that there are no empty cells.'
        except:
            pass

        try:
            # Check that all uploaded tournaments exists (City Year)
            df['tournament_city_year_combo'] = ( df['tournament_city'].apply(lambda x: x.lower()) + ' ' + df['tournament_year'].apply(lambda x: str(int(x))) )
            tournament_city_year_uploaded = df['tournament_city_year_combo'].unique().tolist()
            tournament_city_year_existing = [ f'{ t["City"].lower() } { t["Year"] }' for t in tournaments ]
            tournaments_that_dont_exist = [ t for t in tournament_city_year_uploaded if t not in tournament_city_year_existing ]
            if len(tournaments_that_dont_exist) > 0:
                upload_error_message = f'The following tournaments do not exist: { ", ".join(tournaments_that_dont_exist).title() }. Make sure that all uploaded tournament cities and corresponding years exist. '

            tournament_id_lookup = { f'{ t["City"].lower() } { t["Year"] }': t['ID'] for t in tournaments }
            df['Tournament_id'] = df['tournament_city_year_combo'].map(tournament_id_lookup)
        except:
            pass

        try:
            # Check that all uploaded teams exists (City TeamName)
            df['team_city_name_combo'] = ( df['player_team_city'].apply(lambda x: x.lower()) + ' ' + df['player_team_name'].apply(lambda x: x.lower()) )
            team_city_name_uploaded = df['team_city_name_combo'].unique().tolist()
            team_city_name_existing = [ f'{ team["City"].lower() } { team["TeamName"].lower() }' for team in teams ]
            teams_that_dont_exist = [ t for t in team_city_name_uploaded if t not in team_city_name_existing ]
            if len(teams_that_dont_exist) > 0:
                upload_error_message = f'The following tournaments do not exist: { ", ".join(teams_that_dont_exist).title() }. Make sure that all uploaded team cities and corresponding teams exist. '

            team_id_lookup = { f'{ t["City"].lower() } { t["TeamName"].lower() }': t['ID'] for t in teams }
            df['Team_id'] = df['team_city_name_combo'].map(team_id_lookup)
        except:
            pass

        try:
            # Check that all classification values are between 1-5
            classification_values_uploaded = df['player_classification_value'].apply(lambda x: int(x)).unique().tolist()
            classification_values_improper = [ value for value in classification_values_uploaded if value <= 0 or value > 5  ]
            if len(classification_values_improper) > 0:
                upload_error_message = 'All classification_values must be between 1-5, please enter proper classification values.'
        except:
            pass

        try:
            # Check that all player numbers are between 0-99
            player_numbers_uploaded = df['player_number'].apply(lambda x: int(x)).unique().tolist()
            player_numbers_improper = [ value for value in player_numbers_uploaded if value < 0 or value >= 100  ]
            if len(player_numbers_improper) > 0:
                upload_error_message = 'All player_number must be between 0-100, please enter proper player numbers.'
        except:
            pass

        try:
            # Check that all fields have the correct dtype
            df = df.astype(dtype_map)
        except:
            upload_error_message = 'One or more fields are not in the correct format. Please make sure that all integer fields contain only integers.'

        if upload_error_message:
            print(upload_error_message)

            return render(request, 'upload_update.html', {
                    'admin_url': admin_url,
                    'tournaments': tournaments,
                    'teams': teams,
                    'upload_error_message': upload_error_message,
                }
            )

        df = df.astype(dtype_map)

        url_players = f'{ api_base_url }/players/'
        call_players = requests.get(url=url_players)
        players = call_players.json()

        ### Upload New Players ###

        # Check which players don't existws
        df['player_first_last_name_team_id_combo'] = ( df['player_first_name'].apply(lambda x: x.lower()) + ' ' + df['player_last_name'].apply(lambda x: x.lower()) + ' ' + df['Team_id'].apply(lambda x: str(int(x))) )
        player_last_name_team_id_uploaded = df['player_first_last_name_team_id_combo'].tolist()
        player_last_name_team_id_existing = [ f'{ player["PlayerFirstName"].lower() } { player["PlayerLastName"].lower() } { player["Team"]["ID"] }' for player in players ]
        players_that_dont_exist = [ t for t in player_last_name_team_id_uploaded if t not in player_last_name_team_id_existing ]

        df_players_to_upload = df[df['player_first_last_name_team_id_combo'].isin(players_that_dont_exist)][[
            'player_first_name',
            'player_last_name',
            'Team_id',
        ]].rename(columns={
            'player_first_name': 'PlayerFirstName',
            'player_last_name': 'PlayerLastName',
            'Team_id': 'Team',
        })

        data_create_players = df_players_to_upload.to_dict(orient='Records')

        # Upload df_players_to_upload into Players model
        url_create_players = api_base_url + '/create/players/'
        call_create_players = requests.post(
            url = url_create_players,
            json = data_create_players,
            headers = headers,
        )

        create_players = json.loads(call_create_players.content.decode('utf-8'))

        # Refreshes players variable to include newly upload player_ids
        call_players = requests.get(url=url_players)
        players = call_players.json()

        # Adds player_ids to upload records
        player_id_lookup = { f'{ player["PlayerFirstName"].lower() } { player["PlayerLastName"].lower() } { player["Team"]["ID"] }': player['ID'] for player in players }
        df['Player_id'] = df['player_first_last_name_team_id_combo'].map(player_id_lookup).fillna(0).astype('int32')

        ### Upload New Players ###

        df_tournament_player = df[[
            'Tournament_id',
            'Player_id',
            'player_number',
            'player_classification_value',
        ]].rename(columns={
            'Tournament_id': 'Tournament',
            'Player_id': 'Player',
            'player_number': 'PlayerNumber',
            'player_classification_value': 'ClassificationValue',
        })

        # Needs to determine if current player is already in tournament -> adds tournament_player_id if so
        lookup_existing_tournament_player_id = { (t_p['Player']['ID'], t_p['Tournament']['ID']): t_p['id'] for t_p in tournament_players if f'{ t_p["Tournament"]["City"].lower() } { t_p["Tournament"]["Year"] }' in tournament_city_year_existing}

        df_tournament_player['id'] = df_tournament_player.apply(
            lambda row: lookup_existing_tournament_player_id.get((row['Player'], row['Tournament'])),
            axis=1
        ).fillna(0).astype('int32')

        data_create_update_tournament_players = df_tournament_player.to_dict(orient='Records')

        for record in data_create_update_tournament_players:
            keys_to_remove = [key for key, value in record.items() if key == 'id' and value == 0]
            
            for key in keys_to_remove:
                del record[key]

        # Uploads new players in tournament, updates existing players in tournament
        url_create_update_tournament_players = f'{ api_base_url }/create_update/tournament_players/'
        call_create_update_tournament_players = requests.post(
            url = url_create_update_tournament_players,
            json = data_create_update_tournament_players,
            headers = headers,
        )

        create_update_tournament_players = json.loads(call_create_update_tournament_players.content.decode('utf-8'))

        # Adds session variables to show results
        request.session['results_created_players'] = create_players
        request.session['results_created_update_tournament_players'] = create_update_tournament_players

        return redirect('/upload/success/')

    return render(request, 'upload_update.html', {
            'admin_url': admin_url,
            'tournaments': tournaments,
            'teams': teams,
        }
    )

def upload_update_success(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')

    if access_token:
        try:
            jwt.decode(access_token, API_KEY, algorithms='HS256')
        except:
            request.session['previous_url'] = request.path
            return HttpResponseRedirect('/refresh/')

        headers = {
            'Authorization': f'Bearer { access_token }'
        }

    admin_url = None

    if access_token:
        headers = {
            'Authorization': f'Bearer { access_token }'
        }
        try:
            payload = jwt.decode(access_token, API_KEY, algorithms='HS256')
            user_id = payload.get('user_id')

            user = requests.get(url=f'{ api_base_url }/user/{ user_id }', headers=headers).json()
            
            if user['is_staff']:
                admin_url = f'{ api_base_url }/admin'
        except:
            return HttpResponseRedirect('/')

    elif not access_token:
        return HttpResponseRedirect('/')

    try:
        results_created_players = request.session.get('results_created_players', None)
    except:
        results_created_players = None

    try:
        results_created_update_tournament_players = request.session.get('results_created_update_tournament_players', None)
    except:
        results_created_update_tournament_players = None

    return render(request, 'upload_update_success.html', {
            'admin_url': admin_url,
            'results_created_players': results_created_players,
            'results_created_update_tournament_players': results_created_update_tournament_players,
        }
    )

def download_upload_template(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')

    if access_token:
        try:
            jwt.decode(access_token, API_KEY, algorithms='HS256')
        except:
            request.session['previous_url'] = request.path
            return HttpResponseRedirect('/refresh/')

        headers = {
            'Authorization': f'Bearer { access_token }'
        }

    admin_url = None

    if access_token:
        try:
            payload = jwt.decode(access_token, API_KEY, algorithms='HS256')
            user_id = payload.get('user_id')

            user = requests.get(url=f'{ api_base_url }/user/{ user_id }', headers=headers).json()
            
            if user['is_staff']:
                admin_url = f'{ api_base_url }/admin'
        except:
            return HttpResponseRedirect('/')

    elif not access_token:
        return HttpResponseRedirect('/')

    try:
        template_headers = request.session.get('template_headers', None)
    except:
        return HttpResponseRedirect('/upload/')

    if template_headers:
        response = HttpResponse(
            content_type='text/csv',
        )
        
        response['Content-Disposition'] = 'attachment; filename="tournament_player_upload_template.csv"'
        writer = csv.writer(response)
        writer.writerow(template_headers)

        return response
    
    else:
        return HttpResponseRedirect('/upload/')
