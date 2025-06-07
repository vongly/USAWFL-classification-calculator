from django.shortcuts import render, HttpResponseRedirect

from env import api_base_url, token_name
from utils.helpers import get_user_staff_details, delete_session_item

import requests


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
            secure=False,
            samesite='Lax',
        )
        response.set_cookie(
            f'{ token_name }_refresh',
            tokens['refresh'],
            httponly=True,
            secure=False,
            samesite='Lax',
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
        return HttpResponseRedirect('/')
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
                key=f'{ token_name }_access',
                value=tokens['access'],
                httponly=True,
                secure=False,
                samesite='Lax',
            )
            response.set_cookie(
                key=f'{ token_name }_refresh',
                value=tokens['refresh'],
                httponly=True,
                secure=False,
                samesite='Lax',
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