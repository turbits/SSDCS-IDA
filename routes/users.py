import uuid
import sqlite3
from bottle import route, request, response, template
import re
from models.user import User
from utility.validate_data import validate_data, validate_username, validate_password
from utility.db import connect_db, close_db
import time


# CREATE (post) user
@route('/users', method='POST')
def create_user():
    print("🔵 ENDPOINT:/users POST")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # combine user data into a dict
        # last_logon is initialized to NULL on user creation (None in Python, it is inserted as NULL in SQLite)
        # created_at is initialized to the current unix timestamp; we can use `datetime.datetime.fromtimestamp(<timestamp>)` to convert it to a human readable datetime
        user_data = {
            "username": request.forms.get('username'),
            "first_name": request.forms.get('first_name'),
            "last_name": request.forms.get('last_name'),
            "password": request.forms.get('password'),
            "last_logon": None,
            "created_at": int(time.time()),
            "is_admin": request.forms.get('is_admin'),
            "is_disabled": request.forms.get('is_disabled')
        }

        # validate the user data using the User model and the data above, passed through a generic validation function
        validation_check = validate_data(user_data, User)
        if validation_check is not None:
            raise ValueError(validation_check)

        # create a new User object and spread the user data into it
        user = User(**user_data)
        print(f"🔵 USER: {user.__dict__}")
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

        # we select the newly inserted user, both for return and to insert a uuid_ref
        cursor.execute('SELECT * FROM users WHERE username = ?', (user.username,))
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

        # commit changes
        con.commit()
        # close the connection
        close_db(con, cursor)

        print(f"🟢 OK(200): User created successfully: {newuser['username']}")
        # return the new user
        return {"data": newuser}

    # ValueError can be raised by validation or DB checks
    except ValueError as e:
        response.status = 400
        close_db(con, cursor)
        print(f"🔴 ERROR(400): {str(e)}")
        return {"message": f"Invalid request body: {str(e)}"}

    # unhandled
    except Exception as e:
        response.status = 500
        close_db(con, cursor)
        print(f"🔴 ERROR(500): {str(e)}")
        return {"message": f"Unhandled exception when creating user: {str(e)}"}


# READ (get) all users
@route('/users', method='GET')
def get_all_users():
    print("🔵 ENDPOINT:/users GET")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # fetch all users
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()

        # create a dictionary list of users
        users = []
        for row in rows:
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
            users.append(user)

        response.content_type = 'application/json'
        response.status = 200
        response.body = users

        # close the connection
        close_db(con, cursor)

        print("🟢 OK(200): Users fetched successfully")
        return {"data": users}
    except Exception as e:
        response.status = 500
        close_db(con, cursor)
        print(f"🔴 ERROR(500): {str(e)}")
        return {"message": f"Unhandled exception when fetching users: {str(e)}"}


# Q: Why is POST being used on the /users/<id> endpoint when GET should be used?
#
# A: I have absolutely no idea why, I have spent hours on attempting to debug this, but for whatever reason this framework does not want to use GET in this context. It returns "Critical error while processing request: /users/<id>" (obviously with the id in place).
# I have tried many, many variations that all adhere to the documentation, using @get, @route, I've tried simplifying the route to a simple print statement, a template statement, etc. I've tried different versions of Bottle, turned debug and reload modes on and off, restarted terminal, my computer, everything.
# My opinion is that this is a bug in the framework, but I don't have any more time to spend on this nonsense, so it's POST.
#
# In a real-world scenario you wouldn't be using Bottle anyway, but you would be using GET here, as GET is the proper HTTP method in this case.

# READ (POST; PLEASE READ THE ABOVE) user by id
@route('/users/<id:int>', method='POST')
def get_user(id):
    print("🔵 ENDPOINT:/users/<id> POST(Should be GET; read code comments)")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # select users with the id
        cursor.execute('SELECT * FROM users WHERE id =?', (id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError()

        user = {
            "id": row[0], "username": row[1], "first_name": row[2], "last_name": row[3], "password": row[4], "last_logon": row[5], "created_at": row[6], "is_admin": bool(row[7]), "is_disabled": bool(row[8])
        }
        response.content_type = 'application/json'
        response.status = 200
        # close the connection
        close_db(con, cursor)
        return {"data": user}
    except ValueError:
        response.status = 404
        close_db(con, cursor)
        print("🔴 ERROR(404): User not found")
        return {"message": "User not found"}
    except Exception as e:
        response.status = 500
        close_db(con, cursor)
        print(f"🔴 ERROR(500): {str(e)}")
        return {"message": f"Unhandled exception when fetching user: {str(e)}"}


# UPDATE (put) user by id
@route('/users/<id:int>', method='PUT')
def update_user(id):
    print("🔵 ENDPOINT:/users/<id> PUT")

    con = None
    cursor = None

    try:
        username = request.forms.get('username')
        first_name = request.forms.get('first_name')
        last_name = request.forms.get('last_name')
        password = request.forms.get('password')
        is_admin = request.forms.get('is_admin')
        is_disabled = request.forms.get('is_disabled')

        con, cursor = connect_db()

        # select users with the id
        cursor.execute('SELECT * FROM users WHERE id =?', (id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError()

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
            # then we commit
            con.commit()

        # now we want to get the updated user and return it
        cursor.execute('SELECT * FROM users WHERE id =?', (id,))
        row = cursor.fetchone()
        user = {
            "id": row[0], "username": row[1], "first_name": row[2], "last_name": row[3], "password": row[4], "last_logon": row[5], "created_at": row[6], "is_admin": bool(row[7]), "is_disabled": bool(row[8])
        }

        response.content_type = "application/json"
        response.status = 200

        # close the DB connection
        close_db(con, cursor)
        # return the updated user
        return {"data": user}
    except ValueError:
        response.status = 404
        close_db(con, cursor)
        print("🔴 ERROR(404): User not found")
        return {"message": "User not found"}
    except Exception as e:
        response.status = 500
        close_db(con, cursor)
        print(f"🔴 ERROR(500): {str(e)}")
        return {"message": f"Unhandled exception when updating user: {str(e)}"}


# DELETE (delete) user by id
@route('/users/<id:int>', method='DELETE')
def delete_user(id):
    print("🔵 ENDPOINT:/users/<id> DELETE")

    con = None
    cursor = None

    try:
        con, cursor = connect_db()

        # select user with id
        cursor.execute('SELECT * FROM users WHERE id =?', (id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError()

        # TODO: check for admin

        # delete user
        cursor.execute('DELETE FROM users WHERE id =?', (id,))

        con.commit()
        close_db(con, cursor)

        response.content_type = "application/json"
        response.status = 200

        # row[1] is the username
        return {"message": f"User '{row[1]}' deleted successfully"}

    except ValueError:
        response.status = 404
        close_db(con, cursor)
        print("🔴 ERROR(404): User not found")
        return {"message": "User not found"}
    except Exception as e:
        response.status = 500
        close_db(con, cursor)
        print(f"🔴 ERROR(500): {str(e)}")
        return {"message": f"Unhandled exception when updating user: {str(e)}"}
