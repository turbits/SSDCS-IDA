import sqlite3
import os
import uuid
import time

# QOL: add a warning/confirmation if the database file already exists

# check if database file exists;
# if it does we delete it, recreate it, and reseed it
try:
    os.remove("ida/ida.db")
except OSError:
    pass

# connect to the database; this will create the database file if it doesnt exist
con = sqlite3.connect("ida/ida.db")
cursor = con.cursor()

# ===================== USERREF TABLE =====================
# This is a table that stores a UUID and a user id (foreign key)
#
# Q: What is this used for?
# A: This is to avoid not using a more complex session system (for simplicity) and to allow for a more secure way of authenticating users other than just storing all of the user data in a cookie (plain text)
# When a user is created, a UUID is generated and stored in this table alongside the user ID
# When an API request is made, the UUID is sent in the request header (the cookie) and the user is queried to check if they are flagged as an admin on the backend.
# In a real-world scenario, a sessions library or other framework should probably be used

# CREATE USER_REF TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS user_ref (id INTEGER PRIMARY KEY AUTOINCREMENT, uuid TEXT, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")

# ===================== USERS TABLE =====================
# see models/user for the User model
# CREATE USERS TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, first_name TEXT, last_name TEXT, password TEXT, last_logon INTEGER, created_at INTEGER, is_admin BOOLEAN, is_disabled BOOLEAN)")

# CREAT DEFAULT ADMIN
cursor.execute("INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ('admin', 'Default', 'Admin', 'admin123', None, int(time.time()), True, False,))
# get admin id
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
admin = cursor.fetchone()
admin_id = admin[0]
admin_username = admin[1]
# add user_ref entry
cursor.execute("INSERT INTO user_ref (uuid, user_id) VALUES (?, ?)", (str(uuid.uuid4()), admin_id,))

# CREATE TESTUSER
cursor.execute("INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ('testuser', 'Test', 'User', 'testuser123', None, int(time.time()), False, False,))
# get testuser id
cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
user = cursor.fetchone()
user_id = user[0]
user_username = user[1]
# add user_ref entry
cursor.execute("INSERT INTO user_ref (uuid, user_id) VALUES (?, ?)", (str(uuid.uuid4()), user_id,))

# ===================== RECORDS TABLE =====================
# see models/record for the Record model
# CREATE RECORDS TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_at DATETIME, revised_at DATETIME, file TEXT)")
# seed with some data
cursor.execute("INSERT INTO records (name, created_at, revised_at, file) VALUES (?, ?, ?, ?)", ('Record 1', int(time.time()), None, "{'data': 'Record 1'}",))

# ===================== LOGS TABLE =====================
# see models/log_event for the LogEvent model
# CREATE LOGS TABLE
cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, message TEXT, created_at DATETIME, author_id INTEGER, author_name TEXT)")
# add initial LogEvent
cursor.execute("INSERT INTO logs (level, message, created_at, author_id, author_name) VALUES (?, ?, ?, ?, ?)", ('INFO', 'Initial LogEvent', int(time.time()), admin_id, admin_username,))

# COMMIT & CLOSE con
con.commit()
con.close()
