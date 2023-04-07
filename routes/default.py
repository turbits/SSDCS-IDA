import time
import json
from bottle import template, route, request, response, redirect
from utility.validate_data import validate_username, validate_password
from ida import ida_app
from utility.db import connect_db, close_db
from utility.logger import endpoint_hit
from utility.enums import LogEndpoint, LogMode, LogLevel
import requests


# GETs
@ida_app.route('/', method='GET')
def render_index():
    endpoint_hit(LogEndpoint.INDEX, LogMode.GET)

    cookie_uuid = request.get_cookie('session_uuid')
    cookie_username = request.get_cookie('username')
    session_uuid = None

    # if theres user cookies, check validity
    con, cursor = connect_db()
    cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (cookie_uuid,))
    row = cursor.fetchone()
    close_db(con)

    if row is not None:
        session_uuid = row[1]

    if session_uuid is not None:
        # if the session_uuid is valid, render index with user data
        return template('templates/index.tpl', error=None, success=None, session_uuid=cookie_uuid, username=cookie_username)

    # otherwise, render index without user data
    return template('templates/index.tpl', error=None, success=None, session_uuid=None, username=None, data=None)


@ida_app.route('/login', method='GET')
def render_login():
    endpoint_hit(LogEndpoint.LOGIN, LogMode.GET)

    session_uuid = request.get_cookie('session_uuid')
    print(f"🔵 INFO: Session UUID: {session_uuid} (from cookie)")

    # if there is a session_uuid cookie, redirect to index
    if session_uuid is not None:
        redirect('/')

    # otherwise, render the login page
    return template('templates/login/index.tpl', error=None, success=None, session_uuid=None, username=None, data=None)


@ida_app.route('/login', method='POST')
def login():
    endpoint_hit(LogEndpoint.INDEX, LogMode.POST)

    user_id = None
    user_username = None
    user_pw = None

    # get the username and password from the form
    username = request.forms.get('username')
    password = request.forms.get('password')

    # validate username and pw
    _username_check = validate_username(username)
    _password_check = validate_password(password)

    # if either of the checks fail, return an error
    if _username_check is not True or _password_check is not True:
        print("🔴 ERROR: Failed Regex: Invalid username or password.")
        return template('templates/login/index.tpl', error='Invalid username or password.', success=None, session_uuid=None, username=None, data=None)

    con, cursor = connect_db()
    # if checks pass, find the user in the DB by username
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    close_db(con)

    if row is not None:
        user_id = row[0]
        user_username = row[1]
        user_pw = row[4]

    # if user exists, check if the password matches
    if user_pw != password or user_id is None:
        print("🔴 ERROR: Failed Login: Invalid username or password.")
        return template('templates/login/index.tpl', error='Invalid username or password.', success=None, session_uuid=None, username=None, data=None)

    # if the password matches, fetch user's UUID via user_ref table
    con, cursor = connect_db()
    cursor.execute('SELECT * FROM user_ref WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    close_db(con)

    session_uuid = row[1]

    # if the UUID is not found, return an error
    if session_uuid is None:
        print("🔴 ERROR: Failed Login: Internal server error. (UUID not found)")
        return template('templates/login/index.tpl', error='Internal server error.', success=None, session_uuid=None, username=None, data=None)

    # if we were to harden this, we could add the 'domain' parameter, among others: https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/ (Nadalin, 2018)

    # cookies
    cookie_uuid = str(session_uuid)
    cookie_username = str(user_username)

    print(f"🔵 INFO: Setting cookies: uuid: {session_uuid}\nusername: {user_username}")

    response.set_cookie('session_uuid', cookie_uuid, path='/', max_age=3600)
    response.set_cookie('username', cookie_username, path='/', max_age=3600)

    # redirect to index
    print("redirect to index")
    redirect('/')


@ida_app.route('/logout', method='GET')
def render_logout():
    endpoint_hit(LogEndpoint.LOGOUT, LogMode.GET)

    # delete cookies for site
    response.delete_cookie('session_uuid', path='/')
    response.delete_cookie('username', path='/')

    print("🔵 INFO: cleared cookies.")

    time.sleep(1)
    return template('templates/index.tpl', error=None, success="You've been logged out.", session_uuid=None, username=None, data=None)


@ida_app.route('/dashboard', method='GET')
def render_dashboard():
    endpoint_hit(LogEndpoint.DASHBOARD, LogMode.GET)

    # get the session_uuid cookie
    session_uuid = request.get_cookie('session_uuid')
    print(f"🔵 INFO: Session UUID: {session_uuid} (from cookie)")

    is_admin = False
    # the data that we pass to the dashboard
    data = None

    # check if user cookie exists
    if session_uuid is None:
        print("🔴 ERROR: No session UUID, redirecting to login.")
        return template('templates/login/index.tpl', error='Please log in to access the dashboard.', success=None, session_uuid=None, username=None, data=None)
    else:
        try:
            con, cursor = connect_db()
            # see if uuid is valid
            cursor.execute('SELECT * FROM user_ref WHERE uuid = ?', (session_uuid,))
            row = cursor.fetchone()

            # see if user is admin
            cursor.execute('SELECT * FROM users WHERE username = ?', (request.get_cookie('username'),))
            row2 = cursor.fetchone()
            print("closing con")
            close_db(con)
            print("con closed")
            # if user is admin, set is_admin to True
            if row2[7] == 1:
                print("🔵 INFO: User is admin.")
                is_admin = True

            # if uuid is not valid, delete cookies and redirect to login
            if row is None:
                print("🔴 ERROR: Invalid session UUID, redirecting to login.")
                # if uuid is not valid, delete cookies and redirect to login
                response.delete_cookie('session_uuid', path='/')
                response.delete_cookie('username', path='/')
                return template('templates/login/index.tpl', error='Please log in to access the dashboard.', success=None, session_uuid=None, username=None)
            else:
                # if uuid is valid, get data and render dashboard
                try:
                    print("getting data from endpoint")
                    # get response from endpoint
                    res = requests.get("http://localhost:8080/records", timeout=5)

                    print(f"data from endpoint:\n{res.json()}")
                    # if response is OK (200), continue
                    if res.status_code == 200:
                        # decode the response and load it into a json object
                        print("res 200")

                        # this json object is a list of records in the database, we pass this to the template below
                        return template('templates/dashboard/index.tpl', error=None, success=None, session_uuid=request.get_cookie('session_uuid'), username=request.get_cookie('username'), data=res.json())
                    else:
                        print(f"🔴[GET]/dashboard:code:{res.status_code}")
                        # if response is not OK, return an error
                        return template('templates/dashboard/index.tpl', error=f"Code:{res.status_code}\nReason:{res.status_line}", success=None, session_uuid=request.get_cookie('session_uuid'), username=request.get_cookie('username'), data=None)
                except Exception as e:
                    close_db(con)
                    print(f"🔴[GET]/dashboard:Request to '/records':\n {str(e)}")
                # important: ideally, we would implement efficient storing of data retrieved from the DB, in local storage or some other cache so we didn't have to hit the DB every time we wanted to render the dashboard

                # render the dashboard template and pass in our vars
                print("render dashboard")
                print("data: " + str(data))
                return template('templates/dashboard/index.tpl', error=None, success=None, session_uuid=request.get_cookie('session_uuid'), username=request.get_cookie('username'), data=data)
        except Exception as e:
            print(f"🔴 ERROR:/dashboard GET\n{str(e)}")
            return template('templates/login/index.tpl', error='Internal server error.', success=None, session_uuid=None, username=None, data=None)


# Nadalin, A. (2018) Web Security: How to Harden your HTTP cookies. Available at: [https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/](https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/) [Accessed 28 March 2023]
