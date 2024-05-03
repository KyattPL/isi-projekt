import os
import sqlite3


def __create_users_table():
    # Creates a new users file if it doesn't exist
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS USERS
                 (id INTEGER PRIMARY KEY, userEmail TEXT,
                 userCredentials TEXT)
              ''')

    conn.commit()
    conn.close()


def __insert_user(userEmail, userCredentials):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''INSERT INTO USERS (userEmail, userCredentials) VALUES (?, ?)''',
              (userEmail, userCredentials))

    conn.commit()
    conn.close()


def insert_user_into_db(userEmail, userCredentials):
        __create_users_table()
        __insert_user(userEmail, userCredentials)