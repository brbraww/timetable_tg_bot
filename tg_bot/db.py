import sqlite3


def ensure_connection(func):
    def inner(*args, **kwargs):
        with sqlite3.connect('test.db') as conn:
            res = func(*args, conn=conn, **kwargs)
        return res
    return inner


@ensure_connection
def init_db(conn, forse: bool = False):
    c = conn.cursor()
    if forse:
        c.execute('DROP TABLE IF EXISTS user_message')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_message (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            day         TEXT NOT NULL,
            text        TEXT NOT NULL
        )
    ''')
    conn.commit()


@ensure_connection
def add_message(conn, user_id: int, day: str, text: str):
    c = conn.cursor()
    c.execute('INSERT INTO user_message (user_id, day, text) VALUES (?, ?, ?)', (user_id, day, text))
    conn.commit()


@ensure_connection
def count_messages(conn, user_id: int):
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_message WHERE user_id = ?', (user_id, ))
    (res, ) = c.fetchall()
    return res


@ensure_connection
def list_messages(conn, user_id: int, limit: int = 10):
    c = conn.cursor()
    c.execute('SELECT day, text FROM user_message WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
    return c.fetchall()


@ensure_connection
def day_list(conn, user_id: int, day: str):
    c = conn.cursor()
    c.execute('SELECT text FROM user_message WHERE user_id = ? and day = ?', (user_id, day))
    return c.fetchall()


@ensure_connection
def delete_day_values(conn, user_id: int, day: str):
    c = conn.cursor()
    c.execute('DELETE FROM user_message WHERE user_id = ? and day = ?', (user_id, day))
    conn.commit()