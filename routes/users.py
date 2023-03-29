import uuid
import sqlite3
from bottle import route, request, response, post, get, put, delete
import re
from models.user import User
from utility.validate_data import validate_data, validate_username, validate_password
import time


# CREATE (post) user
@post('/users')
def create_user():
    print("🔵 ENDPOINT:POST /USERS")

    connection = None
    cursor = None

    try:
        connection = sqlite3.connect("ida.db")
        cursor = connection.cursor()
        print("🟢 OK(DB): Connected to database.")
    except:
        print("🔴 ERROR(DB): Could not connect to database.")
        return {"status": "ERROR", "message": "Could not connect to database."}

    try:
        # combine user data into a dict
        # last_logon is initialized to NULL on user creation (None in Python, it is inserted as NULL in SQLite)
        # created_at is initialized to the current unix timestamp; we can use `datetime.datetime.fromtimestamp(<timestamp>)` to convert it to a human readable datetime
        user_data = {
            "username": request.forms.get('username'),
            "first_name": request.forms.get('first_name'),
            "last_name": request.forms.get('last_name'),
            "password": request.forms.get('password'),
            "last_logon": None,
            "created_at": time.time(),
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

        connection.commit()
        print(f"🟢 OK(200): User created successfully: {user.username}")
        return {"status": "OK", "message": f"User created successfully: {user.username}"}

    # ValueError can be raised by validation or DB checks
    except ValueError as e:
        response.status = 400
        print(f"🔴 ERROR(400): {str(e)}")
        return {"status": "ERROR", "message": f"Invalid request body: {str(e)}"}

    # unhandled
    except Exception as e:
        response.status = 500
        print(f"🔴 ERROR(500): {str(e)}")
        return {"status": "ERROR", "message": f"Unhandled exception when creating user: {str(e)}"}

    # close the connection
    connection.close()


# READ (get) all users
@get('/users')
def get_all_users():
    print("🔵 ENDPOINT:GET /USERS")

    connection = None
    cursor = None

    try:
        connection = sqlite3.connect("ida.db")
        cursor = connection.cursor()
        print("🟢 OK(DB): Connected to database.")
    except:
        print("🔴 ERROR(DB): Could not connect to database.")
        return {"status": "ERROR", "message": "Could not connect to database."}

    try:
        # fetch all users
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        
        print(rows)

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
                "is_admin": row[7],
                "is_disabled": row[8]
            }
            users.append(user)

        response.content_type = 'application/json'
        response.status = 200
        response.body = users
        print("🟢 OK(200): Users fetched successfully")
        return {"status": "OK", "message": "Users fetched successfully", "data": users}
    except Exception as e:
        response.status = 500
        print(f"🔴 ERROR(500): {str(e)}")
        return {"status": "ERROR", "message": f"Unhandled exception when fetching users: {str(e)}"}

    # close the connection
    connection.close()


# # READ (get) user by id
# @route('/users/<id>', method="GET")
# def get_user(id):
#     print("🔵 USERS_ENDPOINT:GET_USER(ID)")
#     pass


# # UPDATE (patch) user by id
# @route('/users/<id>', method='PATCH')
# def update_user(id):
#     print("🔵 USERS_ENDPOINT:UPDATE_USER(ID)")
#     pass


# # DELETE (delete) user by id
# @route('users/<id>', method='DELETE')
# def delete_user(id):
#     print("🔵 USERS_ENDPOINT:DELETE_USER(ID)")
#     pass
