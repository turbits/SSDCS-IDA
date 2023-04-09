import time
import json
import requests
from flask import Blueprint, request, redirect, render_template, jsonify, make_response, url_for, session, flash
from utility.validate_data import validate_username, validate_password
from utility.db import connect_db, close_db, check_if_user_admin
from utility.logger import endpoint_hit
from utility.enums import LogEndpoint, LogMode, LogLevel

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/', methods=['GET'])
def home():
    endpoint_hit(LogEndpoint.INDEX, LogMode.GET)

    # get session vars
    session_uuid = session['uuid'] if 'uuid' in session else None

    if session_uuid is not None:
        # if there is a session uuid; lets check validity
        con, cursor = connect_db()
        cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session_uuid,))
        row = cursor.fetchone()
        close_db(con)

        if row[1] is None:
            # uuid is invalid; flash session expiry
            # behind the scenes, the uuid is actually invalid (meaning it doesnt exist in the user_ref table as a valid uuid), but we don't want to provide more information to a potential attacker so we provide a more generic error message
            flash('Your session has expired. Please login again.', 'error')
            # remove session vars if they exist
            session.pop('uuid', None)
            session.pop('username', None)
            session.pop('is_admin', None)
        else:
            # the uuid is valid; lets just render the dashboard
            return render_template('index.jinja', session=session)
    else:
        # there is no session uuid; clear any lingering session vars
        session.pop('uuid', None)
        session.pop('username', None)
        session.pop('is_admin', None)
    # render the index page
    return render_template('index.jinja', session=session)


@pages_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        endpoint_hit(LogEndpoint.LOGIN, LogMode.GET)
        session_is_admin = check_if_user_admin(session['username']) if 'username' in session else False
        session['is_admin'] = session_is_admin

        # if there is a uuid in session, redirect to index
        if 'uuid' in session:
            flash('You are already logged in.')
            return redirect(url_for('pages.home'))

        # otherwise, render the login page
        # res = make_response(render_template('login/index.jinja'))
        # return res
        return render_template('login/index.jinja')
    elif request.method == 'POST':
        endpoint_hit(LogEndpoint.LOGIN, LogMode.POST)

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
            return render_template('login/index.jinja', session=session)

        # if the credentials match, fetch the user's uuid from the user_ref table
        cursor.execute('SELECT * FROM user_ref WHERE user_id =?', (id_from_db,))
        row2 = cursor.fetchone()
        close_db(con)
        # set session var with uuid or None if no row is returned
        session['uuid'] = row2[1] if row2 is not None else None

        if session['uuid'] is None:
            # if the uuid is not found in the database, rerender login and return an error
            # we make this error generic as we don't want to provide contextual information to an attacker
            # "internal server error" is much less useful to an attacker than "user not found"
            close_db(con)
            flash('Internal server error.', 'error')
            return render_template('login/index.jinja', session=session)

        # one last sanity check to make sure the user exists and the user values are not None
        if username_from_db is None or password_from_db is None or id_from_db is None or session['uuid'] is None:
            # if any of the values are None, rerender login and return an error
            flash('Internal server error.', 'error')
            return render_template('login/index.jinja', session=session)

        # user has been authenticated, and the session_uuid is validated!
        # set remaining session vars and redirect to the home page
        session['username'] = str(username_from_db)
        session['is_admin'] = check_if_user_admin(session['username'])
        flash('You have successfully logged in.', 'success')
        print("logged in; redirecting to home")
        return redirect(url_for('pages.home'))
    else:
        flash('Method not allowed.', 'error')
        return redirect(url_for('pages.login'))


@pages_bp.route('/logout', methods=['GET'])
def logout():
    endpoint_hit(LogEndpoint.LOGOUT, LogMode.GET)

    # clear session cookies
    session.pop('uuid', None)
    session.pop('username', None)
    flash('You have successfully logged out.', 'success')
    time.sleep(1)
    return redirect(url_for('pages.home'))


@pages_bp.route('/dashboard', methods=['GET'])
def dashboard():
    endpoint_hit(LogEndpoint.DASHBOARD, LogMode.GET)

    # get session vars
    session_uuid = session['uuid'] if 'uuid' in session else None

    # if the session_uuid is None, redirect to login
    if session_uuid is None:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))
    else:
        try:
            con, cursor = connect_db()
            # see if uuid is valid
            cursor.execute('SELECT * FROM user_ref WHERE uuid = ?', (session_uuid,))
            row = cursor.fetchone()
            close_db(con)

            # if uuid is not valid, delete cookies and redirect to login
            if row is None:
                session.pop('uuid', None)
                session.pop('username', None)
                session.pop('is_admin', None)
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('pages.login'))
            else:
                # uuid is valid; continue
                records = requests.get("http://127.0.0.1:8080/records", timeout=5)
                return render_template('dashboard/index.jinja', session=session, data=records.json())
        except Exception as e:
            close_db(con)
            flash(f'{str(e)}', 'error')
            return redirect(url_for('pages.login'))


@pages_bp.route('/usersview', methods=['GET'])
def users_view():
    endpoint_hit(LogEndpoint.USERSVIEW, LogMode.GET)

    # get session vars
    session_uuid = session['uuid'] if 'uuid' in session else None
    session_username = session['username'] if 'username' in session else None
    session_is_admin = check_if_user_admin(session_username) if 'username' in session else False

    # if the session_uuid is None, redirect to login
    if session_uuid is None:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))
    else:
        try:
            con, cursor = connect_db()
            # see if uuid is valid
            cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session_uuid,))
            row = cursor.fetchone()
            close_db(con)

            # if the user is not an admin, redirect to dashboard with error and 401
            if session_is_admin is False:
                flash('You are not authorized to view this page.', 'error')
                return redirect(url_for('pages.dashboard'))

            # if uuid is not valid, delete cookies and redirect to login
            if row is None:
                session.pop('uuid', None)
                session.pop('username', None)
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('pages.login'))
            else:
                # uuid is valid; continue to request the users and render the usersview page if successful
                # TODO: should probably add a try/except here to catch any errors
                res = requests.get("http://127.0.0.1:8080/users", timeout=5)
                users = res if res.status_code == 200 else None
                return render_template('usersview/index.jinja', session=session, data=users.json())
        except Exception as e:
            # if there is an error, flash error and redirect to dashboard
            close_db(con)
            flash(f'{str(e)}', 'error')
            return redirect(url_for('pages.home'))


@pages_bp.route('/logsview', methods=['GET'])
def logs_view():
    endpoint_hit(LogEndpoint.LOGSVIEW, LogMode.GET)

    # get session vars
    session_uuid = session['uuid'] if 'uuid' in session else None
    session_username = session['username'] if 'username' in session else None
    session_is_admin = check_if_user_admin(session_username) if 'username' in session else False

    # if the session_uuid is None, redirect to login
    if session_uuid is None:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('pages.login'))
    else:
        try:
            con, cursor = connect_db()
            # see if uuid is valid
            cursor.execute('SELECT * FROM user_ref WHERE uuid =?', (session_uuid,))
            row = cursor.fetchone()

            close_db(con)

            # if the user is not an admin, redirect to dashboard with error and 401
            if session_is_admin is False:
                flash('You are not authorized to view this page.', 'error')
                return redirect(url_for('pages.dashboard'))

            # if uuid is not valid, delete cookies and redirect to login
            if row is None:
                session.pop('uuid', None)
                session.pop('username', None)
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('pages.login'))
            else:
                # uuid is valid; continue to request the logs and render the logsview page if successful
                # TODO: should probably add a try/except here to catch any errors
                res = requests.get("http://127.0.0.1:8080/logs", timeout=5)
                logs = res if res.status_code == 200 else None
                return render_template('logsview/index.jinja', session=session, data=logs.json())
        except Exception as e:
            close_db(con)
            flash(f'{str(e)}', 'error')
            return redirect(url_for('pages.login'))
