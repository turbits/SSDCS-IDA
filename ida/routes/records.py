import uuid
import sqlite3
import json
import time
import re
import os
import requests
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, make_response, session, abort
from cryptography.fernet import Fernet
from models.record import Record
from utility.validate_data import validate_data
from utility.db import connect_db, close_db
from utility.logger import endpoint_hit
from utility.enums import LogEndpoint, LogMode

records_bp = Blueprint('records', __name__)


@records_bp.before_request
def restrict_access():
    load_dotenv()
    allowed_ips = os.getenv("ALLOWED_IPS").split(",")
    if request.remote_addr not in allowed_ips:
        res = make_response({"message": "You are not authorized to perform this action"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 401
        return res


@records_bp.route('/records', methods=['GET', 'POST'])
def records():
    session_uuid = request.headers.get('uuid', None)
    session_username = request.headers.get('username', None)

    con, cursor = connect_db()

    try:
        if request.method == 'GET':
            endpoint_hit(endpoint=LogEndpoint.RECORDS, mode=LogMode.GET)

            if session_uuid is None or session_username is None:
                abort(401, "You are not authorized to perform this action")

            cursor.execute("SELECT * FROM records")
            rows = cursor.fetchall()
            close_db(con)

            data = []
            for row in rows:
                # converting row to dict and appending to data list
                data.append({
                    'id': row[0],
                    'name': row[1],
                    'created_at': row[2],
                    'revised_at': row[3],
                    'file': row[4]
                })

            res = make_response(jsonify(data))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res

        elif request.method == 'POST':
            # endpoint_hit(LogEndpoint.RECORDS, LogMode.POST)
            load_dotenv()

            IDA_ISS_SHARED_KEY = os.getenv("IDA_ISS_SHARED_KEY")
            if not IDA_ISS_SHARED_KEY:
                raise ValueError("Fernet key not found in .env")
            fernet = Fernet(IDA_ISS_SHARED_KEY.encode())

            x_iss_token = request.headers.get("X-ISS-TOKEN", None)
            env_iss_token = os.getenv("ISS_TOKEN")

            is_iss_making_request = x_iss_token == env_iss_token

            # here we are locking down the endpoint to only allow requests from the ISS microservice
            # the way this works is that the ISS request will include a "token" header; this is a secret token
            # if the token is not present, or does not match the secret token, the request is rejected
            if is_iss_making_request is False:
                res = make_response({"message": "You are not authorized to perform this action"})
                res.headers['Content-Type'] = 'application/json'
                res.status_code = 403
                return res

            # decrypt the data and get back our json object
            payload_encrypted = request.data
            payload_decrypted = fernet.decrypt(payload_encrypted)
            payload_json = json.loads(payload_decrypted)

            print(f"payload_json: {payload_json}")

            # combine record data into a dict
            # revised_at is initialized to NULL on record creation (None in Python, it is inserted as NULL in SQLite)
            # created_at is initialized to the current unix timestamp
            record = {
                "name": payload_json['name'],
                "created_at": int(time.time()),
                "revised_at": None,
                "file": payload_json['file'],
            }

            # validate the record data using the Record model and the data above, passed through a generic validation function
            validation_check = validate_data(record, Record)
            if validation_check is not None:
                raise ValueError("Validation check failed")

            # create a new Record object and spread the record data into it
            record = Record(**record)

            # deserialize the file property
            file_prop = json.dumps(record.file)

            # insert the record into the database
            cursor.execute("INSERT INTO records (name, created_at, revised_at, file) VALUES (?, ?, ?, ?)", (record.name, record.created_at, record.revised_at, file_prop,))
            con.commit()

            # reselect the record from the database once inserted
            cursor.execute("SELECT * FROM records WHERE id =?", (cursor.lastrowid,))
            row = cursor.fetchone()
            # close the db connection
            close_db(con)

            # create record dict from row
            record = {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "revised_at": row[3],
                "file": row[4]
            }

            res = make_response(jsonify(record))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 201
            # return new record
            return res
        else:
            close_db(con)
            abort(405)
    except ValueError as e:
        close_db(con)
        abort(400, str(e))
    except Exception as e:
        close_db(con)
        abort(500, str(e))


@records_bp.route('/records/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def record(id):
    session_uuid = request.headers.get('uuid', None) or request.headers.get('X-UUID', None)
    session_username = request.headers.get('username', None) or request.headers.get('X-USERNAME', None)
    session_is_admin = json.loads(str(request.headers.get('is_admin', False)).lower()) or json.loads(str(request.headers.get('X-IS-ADMIN', False)).lower())
    print(f"session vars from request headers:\nuuid: {session_uuid}\nusername: {session_username}\nis_admin: {session_is_admin}")

    if session_uuid is None or session_username is None:
        abort(401, "You are not authorized to perform this action")

    con, cursor = connect_db()

    try:
        if request.method == 'GET':
            endpoint_hit(LogEndpoint.RECORDS, LogMode.GET, "int:id")

            con, cursor = connect_db()

            # select record with the id
            cursor.execute("SELECT * FROM records WHERE id =?", (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Record not found")

            record = {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "revised_at": row[3],
                "file": row[4],
            }

            # make response object
            res = make_response(jsonify(record))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            # return the record
            return res

        elif request.method == 'PUT':
            endpoint_hit(LogEndpoint.RECORDS, LogMode.PUT, "int:id")

            if session_is_admin is False:
                abort(401, "You are not authorized to perform this action")

            name_prop = request.forms.get('name')
            file_prop = request.forms.get('file_prop')

            # select users with the id
            cursor.execute('SELECT * FROM records WHERE id =?', (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Record not found")

            # some logic to check if any of the fields are empty and if so, to not update that particular field
            updated_fields = {}
            if name_prop is not None:
                updated_fields['name'] = name_prop
            if file_prop is not None:
                updated_fields['file'] = file_prop
            updated_fields['revised_at'] = int(time.time())

            # craft the SQL query based on fields that were updated
            if updated_fields:
                query = 'UPDATE records SET '
                for key, value in updated_fields.items():
                    # for each key value pair that was updated, we add it to the query
                    # for example it would be "UPDATE records SET "
                    # and then we'd add "name =?, " if the name was updated
                    # which would be "UPDATE records SET name =?, "
                    query += f"{key} =?, "
                query = query[:-2] + " WHERE id =?"  # the :-2 removes the last comma and space in the query, then we append the WHERE clause
                values = list(updated_fields.values()) + [id]  # we add the id to the end of the values list
                # we execute our crafted query
                cursor.execute(query, tuple(values))
                # then we commit
                con.commit()

            # now we want to get the updated record and return it
            cursor.execute('SELECT * FROM records WHERE id =?', (id,))
            row = cursor.fetchone()
            close_db(con)

            record = {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "revised_at": row[3],
                "file": row[4]
            }

            res = make_response(jsonify(record))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            # return the updated user
            return res

        elif request.method == 'DELETE':
            endpoint_hit(LogEndpoint.RECORDS, LogMode.DELETE, "int:id")
            print(f"delete/is_admin = {session_is_admin}")

            if session_is_admin is False:
                abort(401, "You are not authorized to perform this action")

            # select record with id
            cursor.execute('SELECT * FROM records WHERE id =?', (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError()
            name = row[1]

            # delete record
            cursor.execute('DELETE FROM records WHERE id =?', (id,))
            # commit changes
            con.commit()
            close_db(con)

            res = make_response({"message": f"Record '{name}' deleted successfully"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200
            return res
        else:
            close_db(con)
            abort(405, "Method not allowed")
    except ValueError as e:
        close_db(con)
        abort(400, str(e))
    except PermissionError as e:
        close_db(con)
        abort(401, str(e))
    except Exception as e:
        close_db(con)
        abort(500, str(e))
