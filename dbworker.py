
import sqlite3


__conection = None


def ensure_connection(func):

    def inner(*args, **kwargs):
        with sqlite3.connect("football.db") as conn:
            res = func(*args, conn=conn, **kwargs)

        return res

    return inner

@ensure_connection
def init_db(conn, force: bool=False):
    c = conn.cursor()


    if force:
        c.execute("DROP TABLE IF EXISTS games")
        c.execute("DROP TABLE IF EXISTS users")
        
    c.execute("""CREATE TABLE IF NOT EXISTS games(
        hour TEXT,
        team_1 TEXT,
        point_1 TEXT,
        point_2 TEXT,
        team_2 TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id TEXT
    )""")

    conn.commit()

@ensure_connection
def add_user(conn, user_id: int):
    c = conn.cursor()
    users = c.execute("SELECT * FROM users")

    if (str(user_id), ) not in users:
        c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    conn.commit()


@ensure_connection
def delete_user(conn, user_id):
    c = conn.cursor()
    return c.execute(f"DELETE FROM users WHERE user_id={user_id}")



@ensure_connection
def get_last_footballs(conn):
    c = conn.cursor()
    return c.execute("SELECT * FROM games")


@ensure_connection
def insert_foot_game(conn, detail):
    c = conn.cursor()
    c.execute(f"""INSERT INTO games VALUES ("{detail[0]}","{detail[1]}","{detail[2]}","{detail[3]}","{detail[4]}")""")

    conn.commit()


@ensure_connection
def get_users(conn):
    c = conn.cursor()
    users = c.execute("SELECT * FROM users").fetchall()
    return users