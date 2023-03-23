import uuid
import sqlite3
from bottle import get, post, delete, route, request, response


connection = sqlite3.connect("ida.db")
cursor = connection.cursor()


# CREATE user
@post('/users')
def create_user():
    # TODO: add try/except
    print("🟢 USERS_ENDPOINT:CREATE")
    _uuid = str(uuid.uuid4())
    data = request.json
    # TODO: write models for data schemas (user, record, and log)
    # TODO: write validation function for req data
    # TODO: write sanitization function for req data

    # TODO: DEBUG REMOVE
    print(data)

    # after validation and sanitization, insert into database
    cursor.execute(f"INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES ('{data.username}', '{data.first_name}', '{data.last_name}', '{data.password}', DATE('now'), DATE('now'), {data.is_admin}, {data.is_disabled})")
    cursor.execute("SELECT id FROM users WHERE username = '{req.username}'")
    user_id = cursor.fetchone()[0]
    cursor.execute(f"INSERT INTO user_ref (uuid, user_id) VALUES ('{_uuid}', {user_id})")


# READ (get) all users
@get('/users')
def get_all_users():
    # fetch all users from database
    pass


# READ (get) user by id
@get('/users/<id>')
def get_user(id):
    pass


# UPDATE (patch in HTTP methods) user by id
@route('/users/<id>', method='PATCH')
def update_user(id):
    pass


# DELETE user by id
@delete('users/<id>')
def delete_user(id):
    pass
