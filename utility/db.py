import sqlite3


def connect_db():
    con = None
    cursor = None

    try:
        con = sqlite3.connect("ida.db")
        cursor = con.cursor()
        print("🔵[SQLITE]: Connected to database")
        return con, cursor
    except sqlite3.Error as e:
        print("🔴 ERROR(DB): Could not connect to database.")
        return {"message": f"Could not connect to database {str(e)}"}


def close_db(con):
    if con is not None:
        con.close()
    return
