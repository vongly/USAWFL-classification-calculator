from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse

from GlobalFunctions import get_user_staff_details, delete_session_item
from env import api_base_url, token_name, API_KEY
import UploadDetails

import requests
import pandas as pd
import json
import csv


def refresh_token(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')

    previous_url = request.session['previous_url']

    try:
        url = f'{ api_base_url }/token/refresh/'
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
    user_staff_details = get_user_staff_details(request)

    if user_staff_details['user']:
        HttpResponseRedirect('/')
    else:
        pass

    if request.method == 'POST':
        form = request.POST

        data_validate_user = {
            'username': form.get('username'),
            'password': form.get('password'),
        }

        call_validate_user = requests.post(
            url=f'{ api_base_url }/token/',
            data=data_validate_user,
        )

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
                    'user_staff_details': user_staff_details,
                    'request': request,
                    'response': response,
                }
            )
        else:
            response = call_validate_user.status_code
            return render(request, 'login.html', {
                    'user_staff_details': user_staff_details,
                    'request': request,
                    'response': response,
                }
            )

    return render(request, 'login.html',{
            'user_staff_details': user_staff_details,
        }
    )



def logout(request):
    user_staff_details = get_user_staff_details(request)

    if user_staff_details['user']:
        response = HttpResponseRedirect('/')
        response.delete_cookie(f'{ token_name }_access')
        response.delete_cookie(f'{ token_name }_refresh')
        return response
    return HttpResponseRedirect('/')



def upload_update(request):
    user_staff_details = get_user_staff_details(request)

    if not user_staff_details['user']['is_staff']:
        HttpResponseRedirect('/')
    elif user_staff_details['user']['is_staff'] and user_staff_details['refresh_required']:
        HttpResponseRedirect('/refresh/')
    else:
        pass

    delete_session_item(request, 'template_headers')
    delete_session_item(request, 'results_created_players')
    delete_session_item(request, 'results_created_update_tournament_players')

    user = user_staff_details['user']
    headers = user_staff_details['headers']

    # For template, allows user to download w/o static file
    expected_columns = UploadDetails.AddUpdateTournamentPlayers.expected_columns
    request.session['template_headers'] = expected_columns

    tournaments = requests.get(url=f'{ api_base_url }/tournaments/').json()
    teams = requests.get(url=f'{ api_base_url }/teams/').json()

    if request.method == 'POST':
        upload_file = request.FILES.get('upload_file')

        if not upload_file:
            return render(request, 'upload_update.html', {
                    'user_staff_details': user_staff_details,
                    'tournaments': tournaments,
                    'teams': teams,
                    'upload_error_message' : 'No File Uploaded',
                }
            )

        # Dataframe
        df = pd.read_csv(upload_file)
        # Clean Dataframe
        df = df.dropna(how='all')
        for column in df.columns:
            df[column.strip().lower()] = df[column].map(lambda x: x.strip() if isinstance(x, str) else x)

        ### Data Validation Checks ###
        upload_file_check = UploadDetails.AddUpdateTournamentPlayers(df, tournaments, teams)

        file_checks = [
            upload_file_check.check_expected_columns(),
            upload_file_check.check_all_fields_correct_dtype(),
            upload_file_check.check_for_blank_cells(),
            upload_file_check.check_if_tournaments_exists(),
            upload_file_check.check_if_tournaments_exists(),
            upload_file_check.check_class_values_between_1_to_5(),
            upload_file_check.check_player_num_between_0_99(),
        ]

        if any(check is not None for check in file_checks):
            for response in file_checks:
                upload_error_message = response
                break

            return render(request, 'upload_update.html', {
                    'user': user,
                    'admin_url': admin_url,
                    'tournaments': tournaments,
                    'teams': teams,
                    'upload_error_message': upload_error_message,
                }
            )

        upload_file_check.add_tournament_id_to_df()
        upload_file_check.add_team_id_to_df()
        upload_file_check.convert_dtype()

        tournament_slugs = upload_file_check.create_tournament_slugs_list()
        team_slugs = upload_file_check.create_team_slugs_list()

        tournament_teams_filter_string = f'?tournament={ "&tournament=".join(tournament_slugs) }&team={ "&team=".join(team_slugs) }'
        tournament_players = requests.get(url=f'{ api_base_url }/tournament_players/{ tournament_teams_filter_string }').json()
        players = requests.get(url=f'{ api_base_url }/players/').json()

        ### Upload New Players ###

        # Check which players don't existws
        df['player_first_last_name_team_id_combo'] = ( df['player_first_name'].apply(lambda x: x.lower()) + ' ' + df['player_last_name'].apply(lambda x: x.lower()) + ' ' + df['team_id'].apply(lambda x: str(int(x))) )
        player_last_name_team_id_uploaded = df['player_first_last_name_team_id_combo'].tolist()
        player_last_name_team_id_existing = [ f'{ player["first_name"].lower() } { player["last_name"].lower() } { player["team"]["id"] }' for player in players ]
        players_that_dont_exist = [ t for t in player_last_name_team_id_uploaded if t not in player_last_name_team_id_existing ]

        df_players_to_upload = df[df['player_first_last_name_team_id_combo'].isin(players_that_dont_exist)][[
            'player_first_name',
            'player_last_name',
            'team_id',
        ]].rename(columns={
            'player_first_name': 'first_name',
            'player_last_name': 'last_name',
            'team_id': 'team',
        })

        data_create_players = df_players_to_upload.to_dict(orient='Records')

        # Upload df_players_to_upload into Players model
        call_create_players = requests.post(
            url = f'{ api_base_url }/players/',
            json = data_create_players,
            headers = headers,
        )

        create_players = json.loads(call_create_players.content.decode('utf-8'))

        # Refreshes players variable to include newly upload player_ids
        players = requests.get(url=f'{ api_base_url }/players/').json()

        # Adds player_ids to upload records
        player_id_lookup = { f'{ player["first_name"].lower() } { player["last_name"].lower() } { player["team"]["id"] }': player['id'] for player in players }
        df['player_id'] = df['player_first_last_name_team_id_combo'].map(player_id_lookup).fillna(0).astype('int32')

        ### Upload New Players ###

        df_tournament_player = df[[
            'tournament_id',
            'player_id',
            'player_number',
            'player_classification_value',
        ]].rename(columns={
            'tournament_id': 'tournament',
            'player_id': 'player',
            'player_number': 'player_number',
            'player_classification_value': 'classification_value',
        })

        # Needs to determine if current player is already in tournament -> adds tournament_player_id if so
        tournament_city_year_existing = upload_file_check.tournament_city_year_existing
        lookup_existing_tournament_player_id = { (t_p['player']['id'], t_p['tournament']['id']): t_p['id'] for t_p in tournament_players if f'{ t_p["tournament"]["city"].lower() } { t_p["tournament"]["year"] }' in tournament_city_year_existing}

        df_tournament_player['id'] = df_tournament_player.apply(
            lambda row: lookup_existing_tournament_player_id.get((row['player'], row['tournament'])),
            axis=1
        ).fillna(0).astype('int32')

        data_create_update_tournament_players = df_tournament_player.to_dict(orient='Records')

        for record in data_create_update_tournament_players:
            keys_to_remove = [key for key, value in record.items() if key == 'id' and value == 0]

            for key in keys_to_remove:
                del record[key]

        # Uploads new players in tournament, updates existing players in tournament
        call_create_update_tournament_players = requests.post(
            url = f'{ api_base_url }/create_update/tournament_players/',
            json = data_create_update_tournament_players,
            headers = headers,
        )

        create_update_tournament_players = json.loads(call_create_update_tournament_players.content.decode('utf-8'))

        # Adds session variables to show results
        request.session['results_created_players'] = create_players
        request.session['results_created_update_tournament_players'] = create_update_tournament_players

        return HttpResponseRedirect('/upload/success/')

    return render(request, 'upload_update.html', {
            'user_staff_details': user_staff_details,
            'tournaments': tournaments,
            'teams': teams,
        }
    )



def upload_update_success(request):
    user_staff_details = get_user_staff_details(request)

    results_created_players = request.session.get('results_created_players', None)
    results_created_update_tournament_players = request.session.get('results_created_update_tournament_players', None)

    tournament_players_created = []
    tournament_players_updated = []

    if results_created_players:
        player_ids = [ str(player['id']) for player in results_created_players ]
        player_ids_string = f'?pid={ "&pid=".join(player_ids) }'

        players_created = requests.get(url=f'{ api_base_url }/players/{ player_ids_string }').json()
    else:
        players_created = []

    if results_created_update_tournament_players:
        if results_created_update_tournament_players['created'] != []:
            tournament_player_ids = [ str(tp['id']) for tp in results_created_update_tournament_players['created'] ]
            tournament_player_ids_string = f'?tpid={ "&tpid=".join(tournament_player_ids) }'

            tournament_players_created = requests.get(url=f'{ api_base_url }/tournament_players/{ tournament_player_ids_string }').json()

        if results_created_update_tournament_players['updated'] != []:
            tournament_player_ids = [ str(tp['id']) for tp in results_created_update_tournament_players['updated'] ]
            tournament_player_ids_string = f'?tpid={ "&tpid=".join(tournament_player_ids) }'

            tournament_players_updated = requests.get(url=f'{ api_base_url }/tournament_players/{ tournament_player_ids_string }').json()

    if not players_created and not tournament_players_created and not tournament_players_updated:
        return HttpResponseRedirect('/upload/')

    return render(request, 'upload_update_success.html', {
            'user_staff_details': user_staff_details,
            'players_created': players_created,
            'tournament_players_created': tournament_players_created,
            'tournament_players_updated': tournament_players_updated,
        }
    )



def download_upload_template(request):
    user_staff_details = get_user_staff_details(request)

    if not user_staff_details['user']['is_staff']:
        HttpResponseRedirect('/')
    elif user_staff_details['user']['is_staff'] and user_staff_details['refresh_required']:
        HttpResponseRedirect('/refresh/')
    else:
        pass

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
