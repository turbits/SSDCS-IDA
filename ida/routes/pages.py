import time
import json
import requests
from flask import Blueprint, request, redirect, render_template, jsonify, make_response, url_for
from utility.validate_data import validate_username, validate_password
from utility.db import connect_db, close_db
from utility.logger import endpoint_hit
from utility.enums import LogEndpoint, LogMode, LogLevel

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/', methods=['GET'])
def home():
    endpoint_hit(LogEndpoint.INDEX, LogMode.GET)

    cookie_uuid = request.cookies.get('session_uuid')
    cookie_username = request.cookies.get('username')

    # if theres user cookies, check validity
    if cookie_uuid is not None:
        con, cursor = connect_db()
        cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (cookie_uuid,))
        row = cursor.fetchone()
        close_db(con)
        # if the session_uuid is valid, render index with user data
        if row is not None and row[1] == cookie_uuid:
            res = make_response(render_template('index.jinja', session_uuid=cookie_uuid, username=cookie_username))
            res.status_code = 200
            # if the session_uuid is valid, render index with user data
            return res

    # otherwise, render index without user data
    res = make_response(render_template('index.jinja'))
    res.status_code = 200
    return res


@pages_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        endpoint_hit(LogEndpoint.LOGIN, LogMode.GET)

        session_uuid = request.cookies.get('session_uuid')
        username = request.cookies.get('username')
        print(f"🔵 INFO: Session UUID: {session_uuid} (from cookie)")

        # if there is a session_uuid cookie, redirect to index
        if session_uuid is not None:
            # res = make_response(redirect('/'))
            res = make_response(render_template('index.jinja', session_uuid=session_uuid, username=username, error='You are already logged in.'))
            return res

        # otherwise, render the login page
        res = make_response(render_template('login/index.jinja'))
        return res
    elif request.method == "POST":
        endpoint_hit(LogEndpoint.INDEX, LogMode.POST)

        user_id = None
        user_username = None
        user_pw = None

        # get the username and password from the form
        username = request.form['username']
        password = request.form['password']

        # validate username and pw
        _username_check = validate_username(username)
        _password_check = validate_password(password)

        # if either of the checks fail, return an error
        if _username_check is not True or _password_check is not True:
            return render_template('login/index.jinja', error='Invalid username or password.')

        con, cursor = connect_db()
        # if checks pass, find the user in the DB by username
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()

        if row is not None:
            user_id = row[0]
            user_username = row[1]
            user_pw = row[4]

        # if user exists, check if the password matches
        if user_pw != password or user_id is None:
            print("🔴 ERROR: Failed Login: Invalid username or password.")
            return render_template('login/index.jinja', error='Invalid username or password.')

        # if the password matches, fetch user's UUID via user_ref table
        cursor.execute('SELECT * FROM user_ref WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        close_db(con)

        session_uuid = row[1]

        # if the UUID is not found, return an error
        if session_uuid is None:
            # we make this error generic as we don't want to provide contextual information to an attacker
            # "internal server error" is much less useful to an attacker than "user not found"
            res = make_response(render_template('login/index.jinja', error='Internal server error'))
            res.status_code = 500
            return res

        # user has been authenticated, the session_uuid is fetched and validated
        # set session cookies and render index
        # if we were to harden our cookies, we could add the 'domain' parameter, among others: https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/ (Nadalin, 2018)
        cookie_uuid = str(session_uuid)
        cookie_username = str(user_username)

        res = make_response(render_template('index.jinja', session_uuid=cookie_uuid, username=cookie_username))
        res.set_cookie('session_uuid', cookie_uuid, path='/', max_age=3600)
        res.set_cookie('username', cookie_username, path='/', max_age=3600)
        res.status_code = 200

        return res
    else:
        res = make_response(render_template('login/index.jinja', error='Invalid request method'))
        res.status_code = 405

        return res


@pages_bp.route('/logout', methods=['GET'])
def logout():
    endpoint_hit(LogEndpoint.LOGOUT, LogMode.GET)

    res = make_response(render_template('index.jinja', success="You've been logged out."))
    res.status_code = 200

    # delete cookies for site
    res.delete_cookie('session_uuid', path='/')
    res.delete_cookie('username', path='/')

    time.sleep(1)

    return res


@pages_bp.route('/dashboard', methods=['GET'])
def dashboard():
    endpoint_hit(LogEndpoint.DASHBOARD, LogMode.GET)

    # get the session_uuid cookie
    session_uuid = request.cookies.get('session_uuid')
    print(f"🔵 INFO: Session UUID: {session_uuid} (from cookie)")

    session_is_admin = False
    # the data that we pass to the dashboard
    data = None

    # if the session_uuid is None, redirect to login
    if session_uuid is None:
        res = make_response(render_template('login/index.jinja', error='Please log in to access the dashboard.'))
        res.status_code = 401
        return res
    else:
        try:
            con, cursor = connect_db()
            # see if uuid is valid
            cursor.execute('SELECT * FROM user_ref WHERE uuid = ?', (session_uuid,))
            row = cursor.fetchone()

            # see if user is admin
            cursor.execute('SELECT * FROM users WHERE username = ?', (request.cookies.get('username'),))
            row2 = cursor.fetchone()
            close_db(con)

            # if user is admin, set session_is_admin to True
            if row2[7] == 1:
                print("🔵 INFO: User is admin.")
                session_is_admin = True

            # if uuid is not valid, delete cookies and redirect to login
            if row is None:
                res = make_response(render_template('login/index.jinja', error='Please log in to access the dashboard.', session_is_admin=session_is_admin, data=data))

                res.delete_cookie('session_uuid', path='/')
                res.delete_cookie('username', path='/')
                res.status_code = 200
            else:
                # uuid is valid; continue
                records = None

                # try:
                print("getting data from endpoint")
                records = requests.get("http://127.0.0.1:8080/records", timeout=5)

                res = make_response(render_template('dashboard/index.jinja', session_uuid=request.cookies.get('session_uuid'), username=request.cookies.get('username'), data=records))
                res.status_code = 200
            return res
        except Exception as e:
            close_db(con)
            res = make_response(render_template('login/index.jinja', error=f'{str(e)}'))
            res.status_code = 500
        finally:
            return res



# Nadalin, A. (2018) Web Security: How to Harden your HTTP cookies. Available at: [https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/](https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/) [Accessed 28 March 2023]
