from django.shortcuts import render, HttpResponseRedirect

from env import api_base_url
from utils.helpers import get_user_staff_details

import requests


def stats(request):
    user_staff_details = get_user_staff_details(request)

    if not user_staff_details['user']['is_staff']:
        return HttpResponseRedirect('/')
    elif user_staff_details['user']['is_staff'] and user_staff_details['refresh_required']:
        return HttpResponseRedirect('/refresh/')
    else:
        pass

    stats = requests.get(url=f'{ api_base_url }/stats/').json()

    if request.method == 'POST':
        form = request.POST
        
        name = form.get('name')
        slug = form.get('slug')
        value = form.get('value')
        value = 1 if value == '' else int(value)

        data = {
            'name': name,
            'slug': slug,
            'value': value,
        }

        response = requests.post(
            f'{ api_base_url }/stats/',
            json=data,
            headers=user_staff_details['headers']
        )

        return HttpResponseRedirect(response)

    return render(request, 'stats.html', {
            'user_staff_details': user_staff_details,
            'stats': stats,
        }
    )
