import uuid
import sqlite3
import time
import re
import json
import requests
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, render_template, make_response, session, abort
from models.user import User
from utility.validate_data import validate_data, validate_username, validate_password
from utility.enums import LogEndpoint, LogMode
from utility.logger import endpoint_hit
from utility.db import connect_db, close_db, check_if_user_admin

users_bp = Blueprint('users', __name__)


@users_bp.before_request
def restrict_access():
    load_dotenv()
    allowed_ips = os.getenv("ALLOWED_IPS").split(",")
    if request.remote_addr not in allowed_ips:
        abort(401, "You are not authorized to perform this action")


@users_bp.route('/users', methods=['GET', 'POST'])
def users():
    session_uuid = request.headers.get('uuid', None) or request.headers.get('X-UUID', None)
    session_username = request.headers.get('username', None) or request.headers.get('X-USERNAME', None)
    session_is_admin = json.loads(str(request.headers.get('is_admin', False)).lower()) or json.loads(str(request.headers.get('X-IS-ADMIN', False)).lower())

    if session_is_admin is False:
        abort(401, "You are not authorized to perform this action")

    con, cursor = connect_db()

    try:
        if request.method == 'GET':
            endpoint_hit(LogEndpoint.USERS, LogMode.GET)

            # fetch all users
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            close_db(con)

            # create a dictionary list of users
            users = []
            for row in rows:
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "password": row[4],
                    "last_logon": row[5],
                    "created_at": row[6],
                    "is_admin": bool(row[7]),
                    "is_disabled": bool(row[8])
                })

            res = make_response(jsonify(users))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res

        elif request.method == 'POST':
            endpoint_hit(LogEndpoint.USERS, LogMode.POST)

            # combine user data into a dict
            # last_logon is initialized to NULL on user creation (None in Python, it is inserted as NULL in SQLite)
            # created_at is initialized to the current unix timestamp; we can use `datetime.datetime.fromtimestamp(<timestamp>)` to convert it to a human readable datetime
            user_data = {
                "username": request.form['username'],
                "first_name": request.form['first_name'],
                "last_name": request.form['last_name'],
                "password": request.form['password'],
                "last_logon": None,
                "created_at": int(time.time()),
                "is_admin": request.form['is_admin'],
                "is_disabled": request.form['is_disabled']
            }

            # validate the user data using the User model and the data above, passed through a generic validation function
            validation_check = validate_data(user_data, User)
            if validation_check is not None:
                raise ValueError("Validation check failed")

            # create a new User object and spread the user data into it
            user = User(**user_data)
            # print(f"🔵 USER: {user.__dict__}")
            # generate a new UUID
            _uuid = str(uuid.uuid4())

            # check if the username exists in DB
            cursor.execute('SELECT COUNT(*) FROM users WHERE username =?', (user.username,))
            _count = cursor.fetchone()
            if _count is not None and _count[0] > 0:
                raise ValueError("Username already exists")

            # check if UUID exists in DB and if it does, generate a new one until it doesn't
            cursor.execute('SELECT COUNT(*) FROM user_ref WHERE uuid =?', (_uuid,))
            _count = cursor.fetchone()
            while _count[0] > 0:
                _uuid = str(uuid.uuid4())
                cursor.execute('SELECT COUNT(*) FROM user_ref WHERE uuid =?', (_uuid,))
                _count = cursor.fetchone()

            # insert and commit the new user to the DB
            cursor.execute('INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user.username, user.first_name, user.last_name, user.password, user.last_logon, user.created_at, user.is_admin, user.is_disabled,))
            con.commit()

            # we select the newly inserted user, both for return and to insert a uuid_ref
            cursor.execute('SELECT * FROM users WHERE username =?', (user.username,))
            row = cursor.fetchone()

            # we create a new user dict of the newly inserted user
            # row = the selected row from "fetchone()"
            # row[0] = the first column in the row, which is the id
            # etc
            # These columns are in the same order as the columns in the users table and as they appear in the User model
            newuser = {
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "password": row[4],
                "last_logon": row[5],
                "created_at": row[6],
                "is_admin": bool(row[7]),
                "is_disabled": bool(row[8])
            }

            # insert and commit the new user_ref to the DB
            cursor.execute('INSERT INTO user_ref (uuid, id) VALUES (?, ?)', (_uuid, newuser['id'],))
            con.commit()
            close_db(con)

            # return response
            res = make_response(jsonify(newuser))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 201
            return res
        # request method is invalid
        else:
            close_db(con)
            abort(405, "Method not allowed")
    except ValueError as e:
        close_db(con)
        abort(400, str(e))
    except Exception as e:
        close_db(con)
        abort(500, str(e))


@users_bp.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def user(id):
    session_uuid = request.headers.get('uuid', None) or request.headers.get('X-UUID', None)
    session_username = request.headers.get('username', None) or request.headers.get('X-USERNAME', None)
    session_is_admin = json.loads(str(request.headers.get('is_admin', False)).lower()) or json.loads(str(request.headers.get('X-IS-ADMIN', False)).lower())
    print(f"session vars from request headers:\nuuid: {session_uuid}\nusername: {session_username}\nis_admin: {session_is_admin}")

    if session_is_admin is False:
        abort(401, "You are not authorized to perform this action")

    con, cursor = connect_db()

    try:
        if request.method == 'GET':
            endpoint_hit(LogEndpoint.USERS, LogMode.GET, "int:id")

            # select users with the id
            cursor.execute('SELECT * FROM users WHERE id =?', (id,))
            row = cursor.fetchone()
            close_db(con)
            if row is None:
                raise ValueError("User not found")

            user = {
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "password": row[4],
                "last_logon": row[5],
                "created_at": row[6],
                "is_admin": bool(row[7]),
                "is_disabled": bool(row[8])
            }

            res = make_response(jsonify(user))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res

        elif request.method == 'PUT':
            endpoint_hit(LogEndpoint.USERS, LogMode.PUT, "int:id")

            username = request.form['username']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            password = request.form['password']
            is_admin = request.form['is_admin']
            is_disabled = request.form['is_disabled']

            # select users with the id
            cursor.execute('SELECT * FROM users WHERE id =?', (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("User not found")

            # some logic to check if any of the fields are empty and if so, to not update that particular field
            updated_fields = {}

            if username is not None:
                updated_fields['username'] = username
            if first_name is not None:
                updated_fields['first_name'] = first_name
            if last_name is not None:
                updated_fields['last_name'] = last_name
            if password is not None:
                updated_fields['password'] = password
            if is_admin is not None:
                updated_fields['is_admin'] = bool(is_admin)
            if is_disabled is not None:
                updated_fields['is_disabled'] = bool(is_disabled)

            updated_fields['updated_at'] = int(time.time())

            # craft the SQL query based on fields that were updated
            if updated_fields:
                query = 'UPDATE users SET '
                for key, value in updated_fields.items():
                    # for each key value pair that was updated, we add it to the query
                    # for example it would be "UPDATE users SET "
                    # and then we'd add "username =?, " if the username was updated
                    # which would be "UPDATE users SET username =?, "
                    query += f"{key} =?, "
                query = query[:-2] + " WHERE id =?"  # the :-2 removes the last comma and space in the query, then we append the WHERE clause
                values = list(updated_fields.values()) + [id]  # we add the id to the end of the values list

                # we execute our crafted query
                user = cursor.execute(query, tuple(values))
                # commit changes
                con.commit()

            # now we want to get the updated user and return it
            cursor.execute('SELECT * FROM users WHERE id =?', (id,))
            row = cursor.fetchone()
            close_db(con)

            user = {
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "password": row[4],
                "last_logon": row[5], 
                "created_at": row[6],
                "is_admin": bool(row[7]),
                "is_disabled": bool(row[8])
            }

            res = make_response(jsonify(user))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res

        elif request.method == 'DELETE':
            endpoint_hit(LogEndpoint.USERS, LogMode.DELETE, "int:id")

            # select user with id
            cursor.execute('SELECT * FROM users WHERE id =?', (id,))
            row = cursor.fetchone()
            username = row[1]
            if row is None:
                raise ValueError("User not found")

            # delete user
            cursor.execute('DELETE FROM users WHERE id =?', (id,))
            con.commit()
            close_db(con)

            res = make_response({"message": f"User '{username}' deleted successfully"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res
        # request method is invalid
        else:
            close_db(con)
            abort(405, "Method not allowed")
    except ValueError as e:
        close_db(con)
        abort(400, str(e))
    except Exception as e:
        close_db(con)
        abort(500, str(e))
