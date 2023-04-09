import uuid
import sqlite3
import re
import time
import json
import requests
from flask import Blueprint, request, jsonify, make_response
from models.log_event import LogEvent
from utility.validate_data import validate_data
from utility.db import connect_db, close_db
from utility.enums import LogEndpoint, LogMode
from utility.logger import endpoint_hit

logs_bp = Blueprint('logs', __name__)

# Because LogEvents are meant to be immutable, i.e. they are read only by anyone except the system, we will not implement create, update, or delete routes or endpoints for LogEvents.

# Instead the system will call internal functions to create LogEvents, and the only endpoints that will be exposed are GET endpoints to fetch all LogEvents or a single LogEvent by id.


# CREATE log function
# NOT an endpoint, but a function that can be called by other endpoints to create a log (see above for explanation)
def create_log(level, message, author_id, author_name):
    endpoint_hit(LogEndpoint.DASHBOARD, LogMode.GET)

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # combine log data into a dict
        # created_at is initialized to the current unix timestamp; we can use `datetime.datetime.fromtimestamp(<timestamp>)` to convert it to a human readable datetime
        log_data = {
            "level": level,
            "message": message,
            "created_at": int(time.time()),
            "author_id": author_id,
            "author_name": author_name,
        }

        # validate the logevent using the LogEvent model and the data above, passed through a generic validation function
        validation_check = validate_data(log_data, LogEvent)
        if validation_check is not None:
            raise ValueError(validation_check)

        # create a new LogEvent object and spread the logevent data into it
        logevent = LogEvent(**log_data)
        # print(f"🔵 LOG: {logevent.__dict__}")

        # insert and commit the logevent to the DB
        cursor.execute('INSERT INTO logs (level, message, created_at, author_id, author_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (logevent.level, logevent.message, logevent.created_at, logevent.author_id, logevent.author_name,))
        con.commit()
        close_db(con)

        res = make_response({"message": "Log created successfully"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 200

        return res

    # ValueError can be raised by validation or DB checks
    except ValueError as e:
        close_db(con)
        res = make_response({"message": f"Invalid request body: {str(e)}"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 400

        return res
    except Exception as e:
        close_db(con)
        res = make_response({"message": f"Unhandled exception when creating logevent: {str(e)}"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 500

        return res


# READ (get) all logs
@logs_bp.route('/logs', methods=['GET'])
def get_all_logs():
    endpoint_hit(LogEndpoint.LOGS, LogMode.GET)

    con = None
    cursor = None
    session_is_admin = False

    try:
        con, cursor = connect_db()

        # see if user is admin
        cursor.execute('SELECT * FROM users WHERE username = ?', (request.cookies.get('username'),))
        row = cursor.fetchone()
        if row is not None and row[7] == 1:
            session_is_admin = True

        if session_is_admin:
            # fetch all logs
            cursor.execute('SELECT * FROM logs')
            rows = cursor.fetchall()
            close_db(con)

            # create a dictionary list of logs
            logevents = []
            for row in rows:
                logevents.append({
                    "id": row[0],
                    "level": row[1],
                    "message": row[2],
                    "created_at": row[3],
                    "author_id": row[4],
                    "author_name": row[5]
                })

                res = make_response(jsonify(logevents))
                res.headers['Content-Type'] = 'application/json'
                res.status_code = 200
                return res
        else:
            close_db(con)
            res = make_response({"message": "You are not authorized to perform this action"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 401
            return res
    except Exception as e:
        close_db(con)
        res = make_response({"message": f"Unhandled exception when fetching logevents: {str(e)}"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 500
        return res


# Please read the comments above the route `@route('/users/<user_id:int>', method='POST')` in routes\users.py for an explanation on why this is a POST request and not a GET request.
# READ (POST, should be GET, read above) log by id
@logs_bp.route('/logs/<int:id>', methods=['GET'])
def get_log(id):
    endpoint_hit(LogEndpoint.LOGS, LogMode.GET, "int:id")

    con = None
    cursor = None
    session_is_admin = False

    try:
        con, cursor = connect_db()

        # see if user is admin
        cursor.execute('SELECT * FROM users WHERE username =?', (request.cookies.get('username'),))
        row = cursor.fetchone()
        if row is not None and row[7] == 1:
            session_is_admin = True

        if session_is_admin is True:
            # select logs with the id
            cursor.execute('SELECT * FROM logs WHERE id =?', (id,))
            row = cursor.fetchone()
            close_db(con)

            if row is None:
                raise ValueError()

            logevent = {
                "id": row[0],
                "level": row[1],
                "message": row[2],
                "created_at": row[3],
                "author_id": row[4],
                "author_name": row[5]
            }

            res = make_response(jsonify(logevent))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res
        else:
            close_db(con)
            res = make_response({"message": "You are not authorized to perform this action"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 401
            return res
    except ValueError:
        close_db(con)
        res = make_response({"message": "LogEvent not found"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 404
        return res
    except Exception as e:
        close_db(con)
        res = make_response({"message": f"Unhandled exception when fetching logevent: {str(e)}"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 500
        return res
