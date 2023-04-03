import time
import json
from bottle import template, route, request, response, redirect
from utility.validate_data import validate_username, validate_password
from ida import ida_app
from utility.db import connect_db, close_db
from urllib import request as urllib_request


# GETs
@ida_app.route('/', method='GET')
def render_index():
    if request.get_cookie('session_uuid') is not None:
        redirect('/dashboard')

    return template('templates/index.tpl', error=None, success=None, session_uuid=None, username=None, data_in=None)


@ida_app.route('/login', method='GET')
def render_login():
    session_uuid = request.get_cookie('session_uuid')

    if session_uuid is not None:
        redirect('/dashboard')

    return template('templates/login/index.tpl', error=None, success=None, session_uuid=None, username=None, data_in=None)


@ida_app.route('/logout', method='GET')
def render_logout():

    # delete cookies for site
    response.delete_cookie('session_uuid')
    response.delete_cookie('username')

    print("🔵 INFO: cleared cookies.")

    time.sleep(1)
    return template('templates/index.tpl', error=None, success="You've been logged out.", session_uuid=None, username=None, data_in=None)


@ida_app.route('/dashboard', method='GET')
def render_dashboard():
    # get the session_uuid cookie
    session_uuid = request.get_cookie('session_uuid')
    is_admin = False
    # the data that we pass to the dashboard
    data = None

    # check if user cookie exists
    if session_uuid is None:
        return template('templates/login/index.tpl', error='Please log in to access the dashboard.', success=None, session_uuid=None, username=None, data_in=None)
    else:
        try:
            con, cursor = connect_db()

            # see if uuid is valid
            cursor.execute('SELECT * FROM user_ref WHERE uuid = ?', (session_uuid,))
            row = cursor.fetchone()

            # see if user is admin
            cursor.execute('SELECT * FROM users WHERE username = ?', (request.get_cookie('username'),))
            row2 = cursor.fetchone()
            if row2[7] == 1:
                is_admin = True

            if row is None:
                # if uuid is not valid, delete cookies and redirect to login
                response.delete_cookie('session_uuid')
                response.delete_cookie('username')
                return template('templates/login/index.tpl', error='Please log in to access the dashboard.', success=None, session_uuid=None, username=None, data_in=None)
            else:
                # if uuid is valid, get data and render dashboard
                # data = cursor.execute('SELECT * FROM records ORDER BY id DESC').fetchall()

                # the url to our records endpoint
                url = 'http://localhost:8080/records'

                # get response from endpoint
                with urllib_request.urlopen(url) as _response:
                    # if response is OK (200), continue
                    if _response.getcode() == 200:
                        # decode the response and load it into a json object
                        _res_str = _response.read().decode('utf-8')
                        # this json object is a list of records in the database, we pass this to the template below
                        data = json.loads(_res_str)
                    else:
                        # if response is not OK, return an error
                        return template('templates/error.tpl', message=f"Error: {_response.getcode()}")

                # important: ideally, we would implement efficient storing of data retrieved from the DB, in local storage or some other cache so we didn't have to hit the DB every time we wanted to render the dashboard

                # render the dashboard template and pass in our vars
                return template('templates/dashboard/index.tpl', error=None, success=None, session_uuid=request.get_cookie('session_uuid'), username=request.get_cookie('username'), data_in=data)
        except Exception as e:
            print(f"🔴 ERROR: {str(e)}")
            return template('templates/login/index.tpl', error='Internal server error.', success=None, session_uuid=None, username=None, data_in=None)


# POSTs
@ida_app.route('/login', method='POST')
def login():
    # get the username and password from the form
    username = request.forms.get('username')
    password = request.forms.get('password')

    # validate username and pw
    _username_check = validate_username(username)
    _password_check = validate_password(password)

    # if either of the checks fail, return an error
    if _username_check is not True or _password_check is not True:
        print("🔴 ERROR: Failed Regex: Invalid username or password.")
        return template('templates/login/index.tpl', error='Invalid username or password.', success=None, session_uuid=None, username=None, data_in=None)

    try:
        con, cursor = connect_db()
        # if checks pass, find the user in the DB by username
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        user_id = row[0]
        user_username = row[1]
        user_pw = row[4]

        # if user exists, check if the password matches
        if user_pw != password or user_id is None:
            print("🔴 ERROR: Failed Login: Invalid username or password.")
            return template('templates/login/index.tpl', error='Invalid username or password.', success=None, session_uuid=None, username=None, data_in=None)

        # if the password matches, fetch user's UUID via user_ref table
        cursor.execute('SELECT * FROM user_ref WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        session_uuid = row[1]

        # if the UUID is not found, return an error
        if session_uuid is None:
            print("🔴 ERROR: Failed Login: Internal server error. (UUID not found)")
            return template('templates/login/index.tpl', error='Internal server error.', success=None, session_uuid=None, username=None, data_in=None)

        # if we were to harden this, we could add the 'domain' parameter, among others: https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/ (Nadalin, 2018)

        # cookies
        cookie_uuid = str(session_uuid)
        cookie_username = str(user_username)

        print(f"🔵 INFO: Setting cookies: uuid: {session_uuid}\nusername: {user_username}")

        response.set_cookie('session_uuid', cookie_uuid, path='/', max_age=3600)
        response.set_cookie('username', cookie_username, path='/', max_age=3600)

        # close the connection
        close_db(con, cursor)

        # return template('templates/dashboard/index.tpl', success='Successfully logged in.', error=None, session_uuid=cookie_uuid, username=cookie_username, data_in=None)
        redirect('/dashboard')

    except Exception as e:
        print(f"🔴 ERROR: {str(e)}")
        return template('templates/login/index.tpl', error='Internal server error.', success=None, session_uuid=None, username=None, data_in=None)

# Nadalin, A. (2018) Web Security: How to Harden your HTTP cookies. Available at: [https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/](https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/) [Accessed 28 March 2023]
