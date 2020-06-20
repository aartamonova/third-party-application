import json

from flask import Blueprint, render_template, request, flash, url_for, make_response, jsonify, session
from flask_api.status import HTTP_403_FORBIDDEN, HTTP_200_OK
from flask_jwt_extended import get_csrf_token, decode_token
from werkzeug.utils import redirect

from config import Config
from third_party_app.third_party_app_utils import get_oauth_by_code_helper, check_login, get_all_tags_helper

bp = Blueprint('index', __name__)


@bp.route('/', methods=['GET'])
def index():
    if not check_login():
        tags = None
    else:
        response = get_all_tags_helper()
        if response.status_code == HTTP_200_OK:
            tags = json.loads(response.content)['tags']
        else:
            tags = None

    return render_template('index.html', tags=tags)


# Перейти на сервис авторизации с кодом приложения
@bp.route('/login/oauth', methods=['GET', 'POST'])
def oauth():
    return redirect(Config.GATEWAY_SERVICE_URL + '/login/oauth?response_type=code' +
                    '&app_id=' + Config.APP_ID + '&redirect_uri=' + Config.APP_URL + '/callback')


@bp.route('/callback', methods=['GET'])
def callback():
    if request.method == 'GET':
        try:
            code = request.args.get('code', type=str)
        except:
            flash('Ошибка авторизации', 'danger')
            return redirect(url_for('index.index'))

        response = get_oauth_by_code_helper(code)
        if response.status_code == HTTP_200_OK:
            try:
                access_token = json.loads(response.content.decode("utf-8"))['access_token']
            except:
                flash('Ошибка авторизации', 'danger')
                return redirect(url_for('index.index'))

            flash('Успешный вход с помощью OAUTH', 'success')
            render_response = make_response(redirect(url_for('index.index')))

            try:
                decoded_token = decode_token(access_token, allow_expired=True)
            except:
                flash('Ошибка авторизации', 'danger')
                return redirect(url_for('index.index'))

            session['access_token'] = access_token
            session['login'] = decoded_token['identity']
            return render_response

        if response.status_code == HTTP_403_FORBIDDEN:
            flash('Неверный логин или пароль', 'danger')
            return redirect(url_for('index.index'))
        else:
            try:
                flash(json.loads(response.data), 'danger')
            except:
                flash('Неизвестная ошибка', 'danger')
            return redirect(url_for('index.index'))


@bp.route('/logout', methods=['GET'])
def logout():
    session['login'] = None
    session['access_token'] = None
    return redirect(url_for('index.index'))
