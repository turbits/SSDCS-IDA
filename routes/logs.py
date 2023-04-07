import uuid
import sqlite3
import re
import time
import json
from bottle import route, request, response, get, template
from models.log_event import LogEvent
from utility.validate_data import validate_data
from utility.db import connect_db, close_db
from ida import ida_app

# Because LogEvents are meant to be immutable, i.e. they are read only by anyone except the system, we will not implement create, update, or delete routes or endpoints for LogEvents.
# Instead the system will call internal functions to create LogEvents, and the only endpoints that will be exposed are GET endpoints to fetch all LogEvents or a single LogEvent by id.


# CREATE log function
# NOT an endpoint, but a function that can be called by other endpoints to create a log (see above for explanation)
def create_log(level, message, author_id, author_name):
    print("🎯[FUNCTION] create_log()")

    con = None
    cursor = None
    is_admin = False

    try:
        con, cursor = connect_db()

        # see if user is admin
        cursor.execute('SELECT * FROM users WHERE username = ?', (request.get_cookie('username'),))
        row = cursor.fetchone()
        if row is not None and row[7] == 1:
            is_admin = True

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

        # commit changes
        con.commit()

        # print to server console
        print(f"🟢 OK(200): Log created for {logevent.message}, initiatior:{logevent.author_name}")

        # close the connection
        close_db(con)
        return

    # ValueError can be raised by validation or DB checks
    except ValueError as e:
        response.status = 400
        if con is not None and cursor is not None:
            close_db(con)
        # print to server console
        print(f"🔴 ERROR(400): {str(e)}")
        # return message
        return {"message": f"Invalid request body: {str(e)}"}

    # unhandled
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when creating logevent: {str(e)}"}


# READ (get) all logs
@ida_app.route('/logs', method="GET")
def get_all_logs():
    print("🎯[GET]/logs")

    con = None
    cursor = None
    is_admin = False

    try:
        con, cursor = connect_db()

        # see if user is admin
        cursor.execute('SELECT * FROM users WHERE username = ?', (request.get_cookie('username'),))
        row = cursor.fetchone()
        if row is not None and row[7] == 1:
            is_admin = True

        # fetch all logs
        cursor.execute('SELECT * FROM logs')
        rows = cursor.fetchall()

        # create a dictionary list of logs
        logevents = []
        for row in rows:
            logevent = {
                "id": row[0],
                "level": row[1],
                "message": row[2],
                "created_at": row[3],
                "author_id": row[4],
                "author_name": row[5]
            }
            logevents.append(logevent)

        logs_json = json.dumps(logevents)

        # print to server console
        print("🟢 OK(200): LogEvents fetched successfully")

        # close the connection
        close_db(con)
        # return message
        return response(logs_json, status=200, content_type="application/json")
    except Exception as e:
        response.status = 500
        response.body = str(e)
        if con is not None and cursor is not None:
            close_db(con)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when fetching logevents: {str(e)}"}


# Please read the comments above the route `@route('/users/<user_id:int>', method='POST')` in routes\users.py for an explanation on why this is a POST request and not a GET request.
# READ (POST, should be GET, read above) log by id
@ida_app.route('/logs/<id:int>', method="POST")
def get_log(id):
    print("🎯[POST]/logs/<id:int>")

    con = None
    cursor = None
    is_admin = False

    try:
        con, cursor = connect_db()

        # see if user is admin
        cursor.execute('SELECT * FROM users WHERE username = ?', (request.get_cookie('username'),))
        row = cursor.fetchone()
        if row is not None and row[7] == 1:
            is_admin = True

        # select logs with the id
        cursor.execute('SELECT * FROM logs WHERE id =?', (id,))
        row = cursor.fetchone()

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

        logevent_json = json.dumps(logevent)

        # print to server console
        print("🟢 OK(200): LogEvent fetched successfully")
        # close the connection
        close_db(con)
        # return response
        return response(logevent_json, status=200, content_type="application/json")
    except ValueError:
        response.status = 404
        if con is not None and cursor is not None:
            close_db(con)
        # print to server console
        print("🔴 ERROR(404): LogEvent not found")
        # return message
        return {"message": "LogEvent not found"}
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when fetching logevent: {str(e)}"}
