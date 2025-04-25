from django.shortcuts import render, HttpResponseRedirect

from env import api_base_url, token_name, API_KEY
from GlobalFunctions import get_user_staff_details

import requests
import jwt

admin_url = None

def TournamentList(request):
    user_staff_details = get_user_staff_details(request)

    tournaments = requests.get(url=f'{ api_base_url }/tournaments/').json()
    tournaments = sorted(tournaments, key=lambda x: x['number'], reverse=True)

    years = sorted(set(item['year'] for item in tournaments), reverse=True)

    return render(request, 'TournamentList.html', {
            'user_staff_details': user_staff_details,
            'tournaments': tournaments,
            'years': years,
        }
    )

def TournamentTeams(request, tournament_slug):
    user_staff_details = get_user_staff_details(request)

    tournament = requests.get(url=f'{ api_base_url }/tournaments/{ tournament_slug }/').json()
    teams_in_tournament = requests.get(url=f'{ api_base_url }/teams/?tournament={ tournament_slug }').json()

    return render(request, 'TournamentTeams.html', {
            'user_staff_details': user_staff_details,
            'teams_in_tournament':teams_in_tournament,
            'tournament':tournament,
        }
    )

def TournamentTeamPlayers(request, tournament_slug, team_slug):
    user_staff_details = get_user_staff_details(request)

    tournament = requests.get(url=f'{ api_base_url }/tournaments/{ tournament_slug }/').json()
    team = requests.get(url=f'{ api_base_url }/teams/{ team_slug }/').json()
    players = requests.get(url=f'{ api_base_url }/tournament_players/?tournament={ tournament_slug }&team={ team_slug }').json()

    if request.method == 'POST':
        if 'clear' in request.POST:
            pass
        elif 'submit' in request.POST:

            submitted_tournamentplayer_ids_strings = request.POST.getlist('players_checked')
            submitted_tournamentplayer_ids = [ int(id) for id in submitted_tournamentplayer_ids_strings ]
            submitted_players = [ player for player in players if player['id'] in submitted_tournamentplayer_ids ]

            classification_values = [ int(player['classification_value']) for player in submitted_players ]

            player_count = len(classification_values)
            classification_total = sum(classification_values)

            submit_details = {
                'player_count' : player_count,
                'classification_total' : classification_total,
            }

            # Handles the ability to maintain a checkmark after form is submitted
            for player in players:
                if player['player']['id'] in submitted_tournamentplayer_ids:
                    player['player_submitted'] = 1 # Maintains Checkmark
                else:
                    player['player_submitted'] = 0 # No Checkmark

            return render(request, 'TournamentTeamPlayers.html', {
                    'user_staff_details': user_staff_details,
                    'players':players,
                    'tournament':tournament,
                    'team':team,
                    'submit_details':submit_details,
                    'submitted_tournamentplayer_ids':submitted_tournamentplayer_ids,
                }
            )

    return render(request, 'TournamentTeamPlayers.html', {
            'user_staff_details': user_staff_details,
            'players':players,
            'tournament':tournament,
            'team':team
        }
    )

