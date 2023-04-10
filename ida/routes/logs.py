import uuid
import sqlite3
import re
import time
import json
import requests
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, make_response, session, abort
from models.log_event import LogEvent
from utility.validate_data import validate_data
from utility.db import connect_db, close_db
from utility.enums import LogEndpoint, LogMode
from utility.logger import endpoint_hit

logs_bp = Blueprint('logs', __name__)


@logs_bp.before_request
def restrict_access():
    load_dotenv()
    allowed_ips = os.getenv("ALLOWED_IPS").split(",")
    if request.remote_addr not in allowed_ips:
        abort(401, "You are not authorized to perform this action")


# READ (get) all logs
@logs_bp.route('/logs', methods=['GET'])
def get_all_logs():
    endpoint_hit(LogEndpoint.LOGS, LogMode.GET)

    session_uuid = request.headers.get('uuid', None)
    session_is_admin = json.loads(str(request.headers.get('is_admin', False)).lower())

    if session_is_admin is False or session_uuid is None:
        abort(401, "You are not authorized to perform this action")

    con, cursor = connect_db()

    try:
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
                "author_username": row[4]
            })

            res = make_response(jsonify(logevents))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res
    except Exception as e:
        abort(500, str(e))


# Please read the comments above the route `@route('/users/<user_id:int>', method='POST')` in routes\users.py for an explanation on why this is a POST request and not a GET request.
# READ (POST, should be GET, read above) log by id
@logs_bp.route('/logs/<int:id>', methods=['GET'])
def get_log(id):
    endpoint_hit(LogEndpoint.LOGS, LogMode.GET, "int:id")

    session_uuid = request.headers.get('uuid', None)
    session_is_admin = json.loads(str(request.headers.get('is_admin', False)).lower())

    if session_is_admin is False or session_uuid is None:
        abort(401, "You are not authorized to perform this action")

    con, cursor = connect_db()

    try:
        # select logs with the id
        cursor.execute('SELECT * FROM logs WHERE id =?', (id,))
        row = cursor.fetchone()
        close_db(con)

        if row is None:
            raise ValueError("logevent not found")

        logevent = {
            "id": row[0],
            "level": row[1],
            "message": row[2],
            "created_at": row[3],
            "author_username": row[5]
        }

        res = make_response(jsonify(logevent))
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 200
        return res
    except ValueError as e:
        close_db(con)
        abort(400, str(e))
    except Exception as e:
        close_db(con)
        abort(500, str(e))
