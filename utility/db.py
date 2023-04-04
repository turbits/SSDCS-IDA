import sqlite3


def connect_db():
    connection = None
    cursor = None

    try:
        connection = sqlite3.connect("ida.db")
        cursor = connection.cursor()
        print("🔵[SQLITE]: Connected to database")
    except sqlite3.Error as e:
        print("🔴 ERROR(DB): Could not connect to database.")
        return {"message": f"Could not connect to database {str(e)}"}

    return connection, cursor


def close_db(con, cursor):
    try:
        print("🔵[SQLITE]: Closing database connection")
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()
    except sqlite3.Error as e:
        print("🔴 ERROR(DB): Could not close database connection.")
        return {"message": f"Could not close database connection {str(e)}"}
