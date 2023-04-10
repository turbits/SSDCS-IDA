import sqlite3


def connect_db():
    con = None
    cursor = None
    try:
        con = sqlite3.connect("ida/ida.db")
        cursor = con.cursor()
        return con, cursor
    except sqlite3.Error as e:
        return {"message": f"Could not connect to database {str(e)}"}


def close_db(con):
    if con is not None:
        con.close()
    return


def check_if_user_admin(username):
    con, cursor = connect_db()
    is_admin = False

    try:
        cursor.execute('SELECT * FROM users WHERE username =?', (username,))
        row = cursor.fetchone()
        # if the row isnt None, and user is admin (row[7]), set is_admin to True
        if row is not None and row[7] == 1:
            is_admin = True
    except Exception as e:
        is_admin = False
        print(f"🔴 ERROR(DB): {str(e)}")
    finally:
        close_db(con)
        print(f"🔏 adminCheck: {username} is admin? {is_admin}")
        return is_admin
