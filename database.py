import sqlite3
import os
import uuid

# TODO: add a warning/confirmation if the database file already exists

# check if database file exists;
# if it does we delete it, recreate it, and reseed it
try:
    os.remove("ida.db")
except OSError:
    pass

# connect to the database; this will create the database file if it doesnt exist
connection = sqlite3.connect("ida.db")
cursor = connection.cursor()

# ===================== USERREF TABLE =====================
# This is a table that stores a UUID and a user id (foreign key)
#
# Q: What is this used for?
# A: This is to avoid not using a more complex session system (for simplicity) and to allow for a more secure way of authenticating users other than just storing the user in a cookie (plain text)
# When a user is created, a UUID is generated and stored in this table alongside the user ID
# When an API request is made, the UUID is sent in the request header (the cookie) and the user is queried to check if they are flagged as an admin on the backend.
# In a real-world scenario, a sessions library or other framework should probably be used

# CREATE USER_REF TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS user_ref (id INTEGER PRIMARY KEY AUTOINCREMENT, uuid TEXT, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")


# con.execute("CREATE TABLE IF NOT EXISTS user_ref (id INTEGER PRIMARY KEY AUTOINCREMENT, uuid TEXT, user_id KEY(user_id) REFERENCES users(id))")

# ===================== USERS TABLE =====================
# CREATE USERS TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, first_name TEXT, last_name TEXT, password TEXT, last_logon DATETIME, created_at DATETIME, is_admin BOOLEAN, is_disabled BOOLEAN)")

# CREAT DEFAULT ADMIN
cursor.execute("INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES ('admin', 'Default', 'Admin', 'admin123', DATE('now'), DATE('now'), 1, 0)")
# get admin id
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
admin_id = cursor.fetchone()[0]
# add user_ref entry
cursor.execute(f"INSERT INTO user_ref (uuid, user_id) VALUES ('{str(uuid.uuid4())}', {admin_id})")

# CREATE TESTUSER
cursor.execute("INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES ('testuser', 'Test', 'User', 'testuser123', DATE('now'), DATE('now'), 0, 0)")
# get testuser id
user_id = cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
user_id = cursor.fetchone()[0]
# add user_ref entry
cursor.execute(f"INSERT INTO user_ref (uuid, user_id) VALUES ('{str(uuid.uuid4())}', {user_id})")

# ===================== RECORDS TABLE =====================
# CREATE RECORDS TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_at DATETIME, revised_at DATETIME, file TEXT)")
# seed with some data
cursor.execute("INSERT INTO records (name, created_at, revised_at, file) VALUES ('Record 1', DATE('now'), DATE('now'), '{''data'': ''Record 1''}')")

# ===================== LOGS TABLE =====================
# CREATE LOGS TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT, message TEXT, created_at DATETIME, author_id INTEGER, author_name TEXT)")
# add initial LogEvent
cursor.execute("INSERT INTO logs (status, message, created_at, author_id, author_name) VALUES ('INFO', 'Initial LogEvent', DATE('now'), 1, 'admin')")

# CLOSE CONNECTION
connection.close()
