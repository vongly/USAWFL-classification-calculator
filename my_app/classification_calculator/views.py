from django.shortcuts import render, HttpResponseRedirect

from env import api_base_url, token_name, API_KEY
from GlobalFunctions import get_user_staff_details, delete_session_item

import requests

from collections import defaultdict
import json

def home(request):
    user_staff_details = get_user_staff_details(request)
    
    return render(request, 'home.html', {
            'user_staff_details': user_staff_details,
        }
    )

def tournament_list(request):
    user_staff_details = get_user_staff_details(request)

    tournaments = requests.get(url=f'{ api_base_url }/tournaments/').json()
    tournaments = sorted(tournaments, key=lambda x: x['number'], reverse=True)

    years = sorted(set(item['year'] for item in tournaments), reverse=True)

    return render(request, 'tournament_list.html', {
            'user_staff_details': user_staff_details,
            'tournaments': tournaments,
            'years': years,
        }
    )

def tournament_teams(request, tournament_slug):
    user_staff_details = get_user_staff_details(request)

    tournament = requests.get(url=f'{ api_base_url }/tournaments/{ tournament_slug }/').json()
    teams_in_tournament = requests.get(url=f'{ api_base_url }/teams/?tournament={ tournament_slug }').json()

    return render(request, 'tournament_teams.html', {
            'user_staff_details': user_staff_details,
            'teams_in_tournament':teams_in_tournament,
            'tournament':tournament,
        }
    )

def tournament_team_players(request, tournament_slug, team_slug):
    user_staff_details = get_user_staff_details(request)
    
    if 'submit_details' in request.session:
        submit_details = request.session['submit_details']
        delete_session_item(request, 'submit_details')
    else:
        submit_details = None

    tournament = requests.get(url=f'{ api_base_url }/tournaments/{ tournament_slug }/').json()
    team = requests.get(url=f'{ api_base_url }/teams/{ team_slug }/').json()
    tournament_players = requests.get(url=f'{ api_base_url }/tournament_players/?tournament={ tournament_slug }&team={ team_slug }').json()
    stats = requests.get(url=f'{ api_base_url }/stats/?active=true/').json()

    teams_in_tournament = requests.get(url=f'{ api_base_url }/teams/?tournament={ tournament_slug }').json()
    possible_opponents = [ team for team in teams_in_tournament if team['slug'] != team_slug ]

    player_stats = requests.get(url=f'{ api_base_url }/player_stats/?tournament={ tournament_slug }&team={ team_slug }').json()

    # Use tuple of frozen keys as a unique group identifier
    group_counts = {}

    for item in player_stats:
        key = (
            json.dumps(item['tournament_player'], sort_keys=True),
            json.dumps(item['stat'], sort_keys=True),
            json.dumps(item['opponent'], sort_keys=True),
        )

        if key not in group_counts:
            group_counts[key] = {
                'tournament_player': item['tournament_player'],
                'stat': item['stat'],
                'opponent': item['opponent'],
                'count': 1,
            }
        else:
            group_counts[key]['count'] += 1

    # Convert to list if needed
    player_stats = list(group_counts.values())

    if request.method == 'POST':
        if 'opponent-selected' in request.POST:
            opponent_selected = int(request.POST.get('opponent-selected'))

            submit_details = {
                'opponent_selected': opponent_selected
            }
            request.session['submit_details'] = submit_details

        else:
            opponent_selected = None

        if 'clear' in request.POST:
            pass
        elif 'submit' in request.POST:

            submitted_tournament_player_ids_strings = request.POST.getlist('players_checked')
            submitted_tournament_player_ids = [ int(id) for id in submitted_tournament_player_ids_strings ]
            submitted_players = [ tournament_player for tournament_player in tournament_players if tournament_player['id'] in submitted_tournament_player_ids ]

            classification_values = [ int(player['classification_value']) for player in submitted_players ]

            player_count = len(classification_values)
            classification_total = sum(classification_values)

            submit_details = {
                'player_count': player_count,
                'classification_total': classification_total,
                'opponent_selected': opponent_selected,
                'submitted_tournament_player_ids': submitted_tournament_player_ids
            }

            request.session['submit_details'] = submit_details

            return HttpResponseRedirect(f'/tournament/{ tournament_slug }/{ team_slug }/')
        return HttpResponseRedirect(f'/tournament/{ tournament_slug }/{ team_slug }/')

    return render(request, 'tournament_team_players.html', {
            'user_staff_details': user_staff_details,
            'tournament_slug': tournament_slug,
            'team_slug': team_slug,
            'tournament':tournament,
            'team':team,
            'tournament_players':tournament_players,
            'stats':stats,
            'possible_opponents': possible_opponents,
            'player_stats': player_stats,
            'submit_details':submit_details,
        }
    )

