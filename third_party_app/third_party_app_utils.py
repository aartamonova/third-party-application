import functools
import json

import requests
from flask import abort, jsonify, make_response, session
from flask_api.status import (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
                              HTTP_500_INTERNAL_SERVER_ERROR, HTTP_504_GATEWAY_TIMEOUT)
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout, Timeout

from config import Config


def response_500_error():
    return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)


def check_login():
    try:
        login = session['login']
    except:
        return False

    if not login:
        return False
    return True


def get_header():
    try:
        access_token = session['access_token']
    except:
        return None
    if not access_token:
        return None
    return {'App-Token': access_token}


def request_error_handler(foo):
    @functools.wraps(foo)
    def wrapper(*args):
        response = None
        try:
            response = foo(*args)
        except ConnectionError:
            response = make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        except (Timeout, ConnectTimeout, ReadTimeout):
            return make_response(jsonify('Истекло время ожидания запроса от сервера'), HTTP_504_GATEWAY_TIMEOUT)
        except:
            abort(404)

        if response.status_code == HTTP_401_UNAUTHORIZED:
            abort(403)
        if response.status_code == HTTP_403_FORBIDDEN:
            return make_response(jsonify('Доступ запрещен'), HTTP_403_FORBIDDEN)
        if response.status_code == HTTP_500_INTERNAL_SERVER_ERROR:
            return make_response(jsonify('В настоящий момент сервис недоступен'), HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == HTTP_400_BAD_REQUEST:
            return make_response(jsonify('Неверные данные. Пожалуйста, '
                                         'проверьте введенные данные '
                                         'и попробуйте еще раз'), HTTP_400_BAD_REQUEST)
        else:
            return response

    return wrapper


@request_error_handler
def get_oauth_by_code_helper(code):
    redirect_uri = Config.APP_URL + '/callback'
    args = {'grant_type': 'authorization_code',
            'app_id': Config.APP_ID,
            'code': code,
            'redirect_uri': redirect_uri}

    service_response = requests.post(Config.GATEWAY_SERVICE_URL + '/oauth/token', json.dumps(args))
    return service_response


@request_error_handler
def get_all_tags_helper():
    headers = get_header()
    if headers:
        response = requests.get(Config.GATEWAY_SERVICE_URL + '/tags/all', headers=headers)
        return response
    return response_500_error()
