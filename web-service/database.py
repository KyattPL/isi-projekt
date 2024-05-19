import os
import sqlite3


def create_snapshot_table():
    conn = sqlite3.connect('snapshot.db')
    c = conn.cursor()

    c.execute('''DROP TABLE IF EXISTS SNAPSHOT''')

    c.execute('''CREATE TABLE IF NOT EXISTS SNAPSHOT
              (champion TEXT PRIMARY KEY, killsAvg REAL, deathsAvg REAL, assistsAvg REAL, expAvg REAL,
              goldAvg REAL, damageDealtAvg REAL, damageTakenAvg REAL, healAvg REAL, csAvg REAL, visionScoreAvg REAL)''')

    conn.commit()
    conn.close()


def insert_champ_to_snapshot(champion, killsAvg, deathsAvg, assistsAvg, expAvg, goldAvg, damageDealtAvg,
                             damageTakenAvg, healAvg, csAvg, visionScoreAvg):
    conn = sqlite3.connect('snapshot.db')
    c = conn.cursor()

    c.execute('''INSERT INTO SNAPSHOT (champion, killsAvg, deathsAvg, assistsAvg, expAvg,
              goldAvg, damageDealtAvg, damageTakenAvg, healAvg, csAvg, visionScoreAvg) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (champion, killsAvg, deathsAvg, assistsAvg, expAvg, goldAvg, damageDealtAvg,
               damageTakenAvg, healAvg, csAvg, visionScoreAvg))

    conn.commit()
    conn.close()


def get_snapshot_data_for_champ():
    pass


def __create_users_table():
    # Creates a new users file if it doesn't exist
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS USERS
                 (id INTEGER PRIMARY KEY, userEmail TEXT,
                 userCredentials TEXT, hasPremium INTEGER)
              ''')

    conn.commit()
    conn.close()


def __insert_user(userEmail, userCredentials):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''INSERT INTO USERS (userEmail, userCredentials, hasPremium) VALUES (?, ?, 0)''',
              (userEmail, userCredentials))

    conn.commit()
    conn.close()


def insert_user_into_db(userEmail, userCredentials):
    __create_users_table()
    __insert_user(userEmail, userCredentials)


def get_user_from_db(userEmail):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM USERS WHERE userEmail = ?''', (userEmail,))
    userObj = c.fetchone()

    conn.commit()
    conn.close()
    return userObj


def get_champ_from_snapshot(champ):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/snapshot.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM SNAPSHOT WHERE champion = ?''', (champ,))
    champStats = c.fetchone()

    conn.commit()
    conn.close()
    return champStats


def update_premium_status_for_email(email, newStatus):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''UPDATE USERS SET hasPremium =? WHERE userEmail =?''',
              (newStatus, email))
    champStats = c.fetchone()

    conn.commit()
    conn.close()
    return


def user_has_premium(email):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/users.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM USERS WHERE userEmail =?''', (email,))
    userObj = c.fetchone()

    conn.commit()
    conn.close()
    return userObj[3] == 1
