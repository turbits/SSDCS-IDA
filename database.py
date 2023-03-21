import sqlite3
import os

# check if database file exists; if it does we delete it, recreate it, and reseed it
try:
    os.remove("ida.db")
except OSError:
    pass

# connect to the database; this will create the database file if it doesnt exist
con = sqlite3.connect("ida.db")

# USERS TABLE
# create the users table if it doesnt exist
con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, first_name TEXT, last_name TEXT, password TEXT, last_logon DATETIME, created_at DATETIME, is_admin BOOLEAN, is_disabled BOOLEAN)")
# create admin user
con.execute("INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES ('admin', 'AdminFirst', 'AdminLast', 'admin123', DATE('now'), DATE('now'), 1, 0)")
# create regular user
con.execute("INSERT INTO users (username, first_name, last_name, password, last_logon, created_at, is_admin, is_disabled) VALUES ('user', 'UserFirst', 'UserLast', 'user123', DATE('now'), DATE('now'), 0, 0)")

# RECORDS TABLE
# create the records table if it doesnt exist
con.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_at DATETIME, revised_at DATETIME, file TEXT)")
# seed with some data
con.execute("INSERT INTO records (name, created_at, revised_at, file) VALUES ('Record 1', DATE('now'), DATE('now'), '{''data'': ''Record 1''}')")

# LOGS TABLE
# create the logs table if it doesnt exist
con.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT, message TEXT, created_at DATETIME, author_id INTEGER, author_name TEXT)")
# add initial LogEvent
con.execute("INSERT INTO logs (status, message, created_at, author_id, author_name) VALUES ('INFO', 'Initial LogEvent', DATE('now'), 1, 'admin')")

# commit changes
con.commit()
