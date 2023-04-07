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


def close_db(con, cursor):
    with con:
        if con is not None:
            con.close()
        if cursor is not None:
            cursor.close()
    return




# try:
#     print("🔵[SQLITE]: Closing database connection")
#     if con is not None:
#         con.close()
#     # if cursor is not None:
#     #     cursor.close()
#     return
# except sqlite3.Error as e:
#     print(f"🔴 ERROR(DB):Couldnt close\n{str(e)}")
#     return {"message": f"Could not close database connection {str(e)}"}
