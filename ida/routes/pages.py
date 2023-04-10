import time
import json
import requests
from flask import Blueprint, request, redirect, render_template, jsonify, make_response, url_for, session, flash
from utility.validate_data import validate_username, validate_password
from utility.db import connect_db, close_db, check_if_user_admin
from utility.logger import endpoint_hit
from utility.enums import LogEndpoint, LogMode, LogLevel

pages_bp = Blueprint('pages', __name__)


# @pages_bp.before_request
# def before_request():
#     excluded_endpoints = ['pages.home']
#     if request.endpoint in excluded_endpoints:
#         return
#     if 'uuid' not in session:
#         return redirect(url_for('pages.home'))


@pages_bp.route('/', methods=['GET'])
def home():
    endpoint_hit(LogEndpoint.HOME, LogMode.GET)

    # get session property
    session_uuid = session['uuid'] if 'uuid' in session else None

    if session_uuid is not None:
        # if there is a session uuid; lets check validity
        con, cursor = connect_db()
        cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session_uuid,))
        row = cursor.fetchone()
        close_db(con)

        # uuid is invalid; flash session expiry and rerender home page
        if row[1] is None:
            print("home/the session uuid is invalid")
            # behind the scenes, the uuid is actually invalid (meaning it doesnt exist in the user_ref table as a valid uuid), but we don't want to provide more information to a potential attacker so we provide a more generic error message
            flash('Your session has expired. Please login again.', 'error')
            # remove session properties if they exist
            session.pop('uuid', None)
            session.pop('username', None)
            session.pop('is_admin', None)
            return render_template('index.jinja')
        else:
            # the uuid is valid; lets just render home page
            return render_template('index.jinja')
    else:
        # there is no session uuid; clear any lingering session properties
        session.pop('uuid', None)
        session.pop('username', None)
        session.pop('is_admin', None)
        # render the home page
        return render_template('index.jinja')


@pages_bp.route('/login', methods=['GET', 'POST'])
def login():
    session_uuid = session['uuid'] if 'uuid' in session else None

    if session_uuid is not None:
        flash('You are already logged in.', 'info')
        return redirect(url_for('pages.home'))

    if request.method == 'GET':
        endpoint_hit(LogEndpoint.LOGIN, LogMode.GET)

        # if there is a uuid in session, redirect to home
        if session_uuid is not None:
            print("login/theres an existing session id; redirecting to home")
            flash('You are already logged in.', 'info')
            return redirect(url_for('pages.home'))
        else:
            # otherwise, render the login page
            return render_template('login/index.jinja')

    elif request.method == 'POST':
        endpoint_hit(LogEndpoint.LOGIN, LogMode.POST)
        # user is attempting to login

        # initialise some vars for verifying user credentials later
        id_from_db = None
        username_from_db = None
        password_from_db = None
        # get the username and password from the form
        username_from_request = request.form['username']
        password_from_request = request.form['password']

        # validate username and pw provided in login form
        _username_check = validate_username(username_from_request)
        _password_check = validate_password(password_from_request)
        # if either of the checks fail, return an error
        if _username_check is not True or _password_check is not True:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('pages.login'))

        # if the validation checks pass, try to find the user in the DB by username
        con, cursor = connect_db()
        cursor.execute('SELECT * FROM users WHERE username =?', (username_from_request,))
        row = cursor.fetchone()
        # if the user exists, fetch the user's ID, username and password from DB
        if row is not None:
            id_from_db = row[0]
            username_from_db = row[1]
            password_from_db = row[4]

        # check if the credentials provided and the credentials fetched from the database match
        if password_from_request != password_from_db or username_from_request != username_from_db:
            # if they dont match, rerender login and return an error
            close_db(con)
            flash('Invalid username or password.', 'error')
            return render_template('login/index.jinja')

        # if the credentials match, fetch the user's uuid from the user_ref table
        cursor.execute('SELECT * FROM user_ref WHERE user_id =?', (id_from_db,))
        row2 = cursor.fetchone()
        close_db(con)
        # set local var to uuid or None if no row is returned
        uuid_from_db = str(row2[1]) if row2 is not None else None
        print(f"login/uuid from db: {uuid_from_db}")

        if uuid_from_db is None:
            # if the uuid is not found in the database, rerender login and return an error
            # we make this error generic as we don't want to provide contextual information to an attacker
            # "internal server error" is much less useful to an attacker than "user not found"
            flash('Internal server error.', 'error')
            return render_template('login/index.jinja')

        # user has been authenticated, and the session_uuid is validated!
        # set remaining session properties and redirect to the home page
        # checking authorization of user and setting local var
        user_is_admin = check_if_user_admin(username_from_db)

        # set our session properties
        session['uuid'] = str(uuid_from_db)
        session['username'] = str(username_from_db)
        session['is_admin'] = user_is_admin

        flash('You have successfully logged in.', 'success')
        return redirect(url_for('pages.home'))
    else:
        flash('Method not allowed.', 'error')
        return redirect(url_for('pages.home'))


@pages_bp.route('/logout', methods=['GET'])
def logout():
    endpoint_hit(LogEndpoint.LOGOUT, LogMode.GET)
    session_uuid = session['uuid'] if 'uuid' in session else None

    if session_uuid is None:
        flash('You are already logged out.', 'info')
        return redirect(url_for('pages.home'))

    # clear session cookies
    session.pop('uuid', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('You have successfully logged out.', 'success')
    time.sleep(1)
    return redirect(url_for('pages.home'))


@pages_bp.route('/recordsview', methods=['GET'])
def records_view():
    endpoint_hit(LogEndpoint.RECORDSVIEW, LogMode.GET)
    session_uuid = session['uuid'] if 'uuid' in session else None
    session_username = session['username'] if 'username' in session else None
    session_is_admin = session['is_admin'] if 'is_admin' in session else False

    # if theres no uuid in the session, redirect to login
    if session_uuid is None:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))

    # validate uuid
    con, cursor = connect_db()
    cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session['uuid'],))
    row = cursor.fetchone()
    close_db(con)
    uuid_is_valid = True if row is not None else False
    # if uuid is not valid, delete session properties and redirect to login
    if uuid_is_valid is False:
        session.pop('uuid', None)
        session.pop('username', None)
        session.pop('is_admin', None)
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))

    try:
        # uuid is valid; continue
        headers = {'uuid': session_uuid, 'username': session_username, 'is_admin': json.dumps(session_is_admin)}
        res = requests.get("http://127.0.0.1:8080/records", timeout=5, headers=headers)
        records = res.json() if res.status_code == 200 else None
        return render_template('recordsview/index.jinja', data=records)
    except Exception as e:
        close_db(con)
        flash(f'{str(e)}', 'error')
        return redirect(url_for('pages.login'))


@pages_bp.route('/usersview', methods=['GET'])
def users_view():
    endpoint_hit(LogEndpoint.USERSVIEW, LogMode.GET)
    session_uuid = session['uuid'] if 'uuid' in session else None
    session_username = session['username'] if 'username' in session else None
    session_is_admin = session['is_admin'] if 'is_admin' in session else False

    # if theres no uuid in the session, redirect to login
    if session_uuid is None:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))

    # user must be admin to access this view
    if session_is_admin is False:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('pages.home'))

    # validate uuid
    con, cursor = connect_db()
    cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session['uuid'],))
    row = cursor.fetchone()
    close_db(con)
    uuid_is_valid = True if row is not None else False
    # if uuid is not valid, delete session properties and redirect to login
    if uuid_is_valid is False:
        session.pop('uuid', None)
        session.pop('username', None)
        session.pop('is_admin', None)
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))

    try:
        # uuid is valid; continue to request the users and render the usersview page if successful
        headers = {'uuid': session_uuid, 'username': session_username, 'is_admin': json.dumps(session_is_admin)}
        res = requests.get("http://127.0.0.1:8080/users", timeout=5, headers=headers)
        users = res.json() if res.status_code == 200 else None
        return render_template('usersview/index.jinja', data=users)
    except Exception as e:
        # if there is an error, flash error and redirect to home
        close_db(con)
        flash(f'{str(e)}', 'error')
        return redirect(url_for('pages.home'))


@pages_bp.route('/logsview', methods=['GET'])
def logs_view():
    endpoint_hit(LogEndpoint.LOGSVIEW, LogMode.GET)
    session_uuid = session['uuid'] if 'uuid' in session else None
    # session_username = session['username'] if 'username' in session else None
    session_is_admin = session['is_admin'] if 'is_admin' in session else False

    # if theres no uuid in the session, redirect to login
    if session_uuid is None:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))

    # user must be admin to access this view
    if session_is_admin is False:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('pages.home'))

    # validate uuid
    con, cursor = connect_db()
    cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session['uuid'],))
    row = cursor.fetchone()
    close_db(con)
    uuid_is_valid = True if row is not None else False
    # if uuid is not valid, delete session properties and redirect to login
    if uuid_is_valid is False:
        session.pop('uuid', None)
        session.pop('username', None)
        session.pop('is_admin', None)
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))

    try:
        # uuid is valid; continue to request the logs and render the logsview page if successful
        headers = {'uuid': session['uuid'], 'username': session['username'], 'is_admin': json.dumps(session['is_admin'])}
        res = requests.get("http://127.0.0.1:8080/logs", timeout=5, headers=headers)
        logs = res.json() if res.status_code == 200 else None
        return render_template('logsview/index.jinja', data=logs)
    except Exception as e:
        # if there is an error, flash error and redirect to home
        close_db(con)
        flash(f'{str(e)}', 'error')
        return redirect(url_for('pages.home'))
