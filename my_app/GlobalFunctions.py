from django.shortcuts import HttpResponseRedirect

import requests
import jwt

from env import api_base_url, API_KEY, token_name

def get_user_staff_details(request):
    access_token = request.COOKIES.get(f'{ token_name }_access')

    headers = None
    user = None
    admin_url = None
    refresh_required = False

    request.session['previous_url'] = request.path
    
    if access_token:
        headers = {
            'Authorization': f'Bearer { access_token }'
        }

        try:
            payload = jwt.decode(access_token, API_KEY, algorithms='HS256')
            user_id = payload.get('user_id')            
            if user_id:
                user = requests.get(url=f'{ api_base_url }/user/{ user_id }', headers=headers).json()            
                if user['is_staff']:
                    admin_url = f'{ api_base_url }/admin'

        except jwt.ExpiredSignatureError:
            refresh_required = True
        except:
            pass

        try:
            payload = jwt.decode(access_token, API_KEY, algorithms='HS256')
        except:
            pass

    user_details = {
        'headers': headers,
        'user': user,
        'admin_url': admin_url,
        'access_token': access_token,
        'refresh_required': refresh_required,
        'api_base_url': api_base_url,
        'token_name': token_name,
    }

    return user_details

def delete_session_item(request, item):
    if item in request.session:
        del request.session[item]
