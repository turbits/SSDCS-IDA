import uuid
import sqlite3
import json
from bottle import route, request, response, template
import re
from models.record import Record
from utility.validate_data import validate_data
from utility.db import connect_db, close_db
import time


# CREATE record
@route('/records', method="POST")
def create_record():
    print("🔵 ENDPOINT:/records POST")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # combine record data into a dict
        # revised_at is initialized to NULL on record creation (None in Python, it is inserted as NULL in SQLite)
        # created_at is initialized to the current unix timestamp; we can use `datetime.datetime.fromtimestamp(<timestamp>)` to convert it to a human readable datetime
        record_data = {
            "name": request.json['name'],
            "created_at": int(time.time()),
            "revised_at": None,
            "file": request.json['file'],
        }

        # validate the record data using the Record model and the data above, passed through a generic validation function
        validation_check = validate_data(record_data, Record)
        if validation_check is not None:
            raise ValueError(validation_check)

        # create a new Record object and spread the record data into it
        record = Record(**record_data)
        # print(f"🔵 RECORD: {record.__dict__}")

        # deserialize the file JSON object
        file_obj = json.dumps(record.file)

        cursor.execute('INSERT INTO records (name, created_at, revised_at, file) VALUES (?, ?, ?, ?)', (record.name, record.created_at, record.revised_at, file_obj,))

        cursor.execute('SELECT * FROM records WHERE id = ?', (cursor.lastrowid,))
        row = cursor.fetchone()

        record = {
            "id": row[0],
            "name": row[1],
            "created_at": row[2],
            "revised_at": row[3],
            "file": row[4]
        }

        # commit changes
        con.commit()

        print(f'🟢 OK(200): Record created successfully: {record["name"]}')

        # close the connection
        close_db(con, cursor)
        # return the new record
        return {"data": record}

    # ValueError can be raised by validation or DB checks
    except ValueError as e:
        response.status = 400
        if con is not None and cursor is not None:
            close_db(con, cursor)
        print(f"🔴 ERROR(400): {str(e)}")
        return {"message": f"Invalid request body: {str(e)}"}

    # unhandled
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con, cursor)
        print(f"🔴 ERROR(500): {str(e)}")
        return {"message": f"Unhandled exception when creating record: {str(e)}"}


# READ (get) all records
@route('/records', method="GET")
def get_all_records():
    print("🔵 ENDPOINT:/records GET")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # fetch all records
        cursor.execute('SELECT * FROM records')
        rows = cursor.fetchall()

        # create a dictionary list of records
        records = []
        for row in rows:
            record = {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "revised_at": row[3],
                "file": row[4],
            }
            records.append(record)

        response.content_type = 'application/json'
        response.status = 200
        response.body = records

        # print to server console
        print("🟢 OK(200): Records fetched successfully")

        # close the connection
        close_db(con, cursor)
        return {"data": records}
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when fetching records: {str(e)}"}


# Please read the comments above the route `@route('/users/<id:int>', method='POST')` in routes\users.py for an explanation on why this is a POST request and not a GET request.
# READ (POST) record by id
@route('/records/<id:int>', method="POST")
def get_record(id):
    print("🔵 ENDPOINT:/records/<id> POST(Should be GET; read code comments)")

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
        response.content_type = 'application/json'
        response.status = 200

        # print to server console
        print(f'🟢 OK(200): Record fetched: {record["name"]}')

        # close the connection
        close_db(con, cursor)
        return {"data": record}
    except ValueError:
        response.status = 404
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print("🔴 ERROR(404): Record not found")
        # return message
        return {"message": "Record not found"}
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when fetching record: {str(e)}"}


# UPDATE (PUT) record by id
@route('/records/<id:int>', method='PUT')
def update_record(id):
    print("🔵 ENDPOINT:/records/<id> PUT")

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
        record = {
            "id": row[0],
            "name": row[1],
            "created_at": row[2],
            "revised_at": row[3],
            "file": row[4]
        }

        response.content_type = "application/json"
        response.status = 200

        # print to server console
        print(f'🟢 OK(200): Record updated: {record["name"]}')

        # close the DB connection
        close_db(con, cursor)
        # return the updated user
        return {"data": record}
    except ValueError:
        response.status = 404
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print("🔴 ERROR(404): Record not found")
        # return message
        return {"message": "Record not found"}
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when updating record: {str(e)}"}


# DELETE record by id
@route('/records/<id:int>', method='DELETE')
def delete_record(id):
    print("🔵 ENDPOINT:/records/<id> DELETE")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # select record with id
        cursor.execute('SELECT * FROM records WHERE id =?', (id,))
        row = cursor.fetchone()
        name = row[1]

        if row is None:
            raise ValueError()

        # TODO: check for admin

        # delete record
        cursor.execute('DELETE FROM records WHERE id =?', (id,))
        # commit changes
        con.commit()

        response.content_type = "application/json"
        response.status = 200

        # print to server console
        print(f'🟢 OK(200): Record deleted: {name}')
        # close connection
        close_db(con, cursor)
        # return message
        return {"message": f"Record '{name}' deleted successfully"}

    except ValueError:
        response.status = 404
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print("🔴 ERROR(404): Record not found")
        # return message
        return {"message": "Record not found"}
    except Exception as e:
        response.status = 500
        if con is not None and cursor is not None:
            close_db(con, cursor)
        # print to server console
        print(f"🔴 ERROR(500): {str(e)}")
        # return message
        return {"message": f"Unhandled exception when updating record: {str(e)}"}
