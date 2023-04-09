import uuid
import sqlite3
import json
import time
import re
import os
import requests
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, make_response
from cryptography.fernet import Fernet
from models.record import Record
from utility.validate_data import validate_data
from utility.db import connect_db, close_db
from utility.logger import endpoint_hit
from utility.enums import LogEndpoint, LogMode

records_bp = Blueprint('records', __name__)


@records_bp.route('/records', methods=['GET', 'POST'])
def records():
    if request.method == 'GET':
        endpoint_hit(LogEndpoint.RECORDS, LogMode.GET)

        con = None
        cursor = None

        # try:
        con, cursor = connect_db()
        cursor.execute('SELECT * FROM records')
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
        endpoint_hit(LogEndpoint.RECORDS, LogMode.POST)

        con = None
        cursor = None

        load_dotenv()

        IDA_ISS_SHARED_KEY = os.getenv("IDA_ISS_SHARED_KEY")
        if not IDA_ISS_SHARED_KEY:
            raise ValueError("Fernet key not found in .env")

        fernet = Fernet(IDA_ISS_SHARED_KEY.encode())

        try:
            con, cursor = connect_db()

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
                raise ValueError(validation_check)

            # create a new Record object and spread the record data into it
            record = Record(**record)

            # deserialize the file property
            file_prop = json.dumps(record.file)

            # insert the record into the database
            cursor.execute('INSERT INTO records (name, created_at, revised_at, file) VALUES (?, ?, ?, ?)', (record.name, record.created_at, record.revised_at, file_prop,))
            con.commit()

            # reselect the record from the database once inserted
            cursor.execute('SELECT * FROM records WHERE id = ?', (cursor.lastrowid,))
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
        except ValueError as e:
            close_db(con)
            res = make_response({"message": f"Invalid request body: {str(e)}"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 400

            return res
        except Exception as e:
            close_db(con)
            res = make_response({"message": f"Unhandled exception when creating record: {str(e)}"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 500

            return res
    else:
        close_db(con)
        res = make_response({"message": "Invalid request method"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 405

        return res


@records_bp.route('/records/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def record(id):
    if request.method == 'GET':
        endpoint_hit(LogEndpoint.RECORDS, LogMode.GET, "int:id")

        con = None
        cursor = None

        try:
            con, cursor = connect_db()

            # select record with the id
            cursor.execute('SELECT * FROM records WHERE id =?', (id,))
            row = cursor.fetchone()

            if row is None:
                raise ValueError()

            record = {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "revised_at": row[3],
                "file": row[4],
            }

            # print to server console
            print(f'🟢 OK(200): Record fetched: {record["name"]}')

            # make response object
            res = make_response(jsonify(record))
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 200

            # return the record
            return res
        except ValueError:
            close_db(con)
            res = make_response({"message": "Record not found"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 404

            return res
        except Exception as e:
            close_db(con)
            res.make_response({"message": f"Unhandled exception when fetching record: {str(e)}"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 500

            return res
    elif request.method == 'PUT':
        endpoint_hit(LogEndpoint.RECORDS, LogMode.PUT, "int:id")

        con = None
        cursor = None

        try:
            name = request.forms.get('name')
            file = request.forms.get('file')

            con, cursor = connect_db()

            # select users with the id
            cursor.execute('SELECT * FROM records WHERE id =?', (id,))
            row = cursor.fetchone()

            if row is None:
                raise ValueError()

            # some logic to check if any of the fields are empty and if so, to not update that particular field
            updated_fields = {}

            if name is not None:
                updated_fields['name'] = name
            if file is not None:
                updated_fields['file'] = file

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
        except ValueError:
            close_db(con)
            res = make_response({"message": "Record not found"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 404

            return res
        except Exception as e:
            close_db(con)
            res = make_response({"message": f"Unhandled exception when updating record: {str(e)}"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 500

            return res
    elif request.method == 'DELETE':
        endpoint_hit(LogEndpoint.RECORDS, LogMode.DELETE, "int:id")

        con = None
        cursor = None
        session_is_admin = False
        username = request.cookies.get('username')
        session_uuid = request.cookies.get('session_uuid')

        if username is None or session_uuid is None:
            res = make_response({"message": "You must be logged in for this action"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 401
            return res

        try:
            con, cursor = connect_db()

            # see if user is admin
            cursor.execute('SELECT * FROM users WHERE username =?', (request.cookies.get('username'),))
            row = cursor.fetchone()
            # checking against [7] which is the 'is_admin' property/column
            if row is not None and row[7] == 1:
                session_is_admin = True

            if session_is_admin is True:
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
                res = make_response({"message": "You are not authorized to perform this action"})
                res.headers['Content-Type'] = 'application/json'
                res.status_code = 401

                return res
        except ValueError:
            close_db(con)
            res = make_response({"message": "Record not found"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 404

            return res
        except Exception as e:
            close_db(con)
            res = make_response({"message": f"Unhandled exception when deleting record: {str(e)}"})
            res.headers['Content-Type'] = 'application/json'
            res.status_code = 500

            return res
    else:
        close_db(con)
        res = make_response({"message": "Invalid request method"})
        res.headers['Content-Type'] = 'application/json'
        res.status_code = 405

        return res
