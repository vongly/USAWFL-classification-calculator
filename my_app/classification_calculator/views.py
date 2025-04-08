from django.shortcuts import render, HttpResponseRedirect

import jwt

from env import api_base_url, token_name, API_KEY
import requests

admin_url = None

def TournamentList(request):
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
            pass

    url = f'{ api_base_url }/tournaments/'
    call = requests.get(url=url)

    tournaments = call.json()    
    tournaments = sorted(tournaments, key=lambda x: x['TournamentNumber'], reverse=True)

    years = sorted(set(item['Year'] for item in tournaments), reverse=True)

    return render(request, 'TournamentList.html', {
            'admin_url':admin_url,
            'tournaments':tournaments,
            'years':years,
        }
    )

def TournamentTeams(request, tournament_slug):
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
            pass

    url_tournament = f'{ api_base_url }/tournaments/{ tournament_slug }/'
    call_tournament = requests.get(url=url_tournament)
    tournament = call_tournament.json()

    url_teams_in_tournament = f'{ api_base_url }/teams/?tournament={ tournament_slug }'
    call_teams_in_tournament = requests.get(url=url_teams_in_tournament)
    teams_in_tournament = call_teams_in_tournament.json()

    return render(request, 'TournamentTeams.html', {
            'admin_url':admin_url,
            'teams_in_tournament':teams_in_tournament,
            'tournament':tournament,
        }
    )

def TournamentTeamPlayers(request, tournament_slug, team_slug):
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
            pass

    url_tournament = f'{ api_base_url }/tournaments/{ tournament_slug }/'
    call_tournament = requests.get(url=url_tournament)
    tournament = call_tournament.json()

    url_team = f'{ api_base_url }/teams/{ team_slug }/'
    call_team = requests.get(url=url_team)
    team = call_team.json()

    url = f'{ api_base_url }/tournament_players/?tournament={ tournament_slug }&team={ team_slug }'
    call = requests.get(url=url)
    players = call.json()

    if request.method == 'POST':
        if 'clear' in request.POST:
            pass
        elif 'submit' in request.POST:

            submitted_tournamentplayer_ids_strings = request.POST.getlist('players_checked')
            submitted_tournamentplayer_ids = [ int(id) for id in submitted_tournamentplayer_ids_strings ]
            

            submitted_players = [ player for player in players if player['id'] in submitted_tournamentplayer_ids ]

            classification_values = [ int(player['ClassificationValue']) for player in submitted_players ]

            player_count = len(classification_values)
            classification_total = sum(classification_values)

            submit_details = {
                'player_count' : player_count,
                'classification_total' : classification_total,
            }

            for player in players:
                if player['Player']['ID'] in submitted_tournamentplayer_ids:
                    player['player_submitted'] = 1
                else:
                    player['player_submitted'] = 0

            return render(request, 'TournamentTeamPlayers.html', {
                    'admin_url':admin_url,
                    'players':players,
                    'tournament':tournament,
                    'team':team,
                    'submit_details':submit_details,
                    'submitted_tournamentplayer_ids':submitted_tournamentplayer_ids,
                }
            )

    return render(request, 'TournamentTeamPlayers.html', {
            'admin_url':admin_url,
            'players':players,
            'tournament':tournament,
            'team':team
        }
    )

