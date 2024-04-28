import os
import sqlite3


def create_notifications_table():
    # Creates a new database file if it doesn't exist
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/notifications.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS NOTIFICATIONS
                 (id INTEGER PRIMARY KEY, userEmail TEXT,
                 userCredentials TEXT, messageSubject TEXT, messageBody TEXT)
              ''')

    conn.commit()
    conn.close()


def insert_notification(userEmail, userCredentials, messageSubject, messageBody):
    path = os.path.join(os.path.dirname(__file__))
    conn = sqlite3.connect(F'{path}/notifications.db')
    c = conn.cursor()

    c.execute('''INSERT INTO NOTIFICATIONS (userEmail, userCredentials, messageSubject, messageBody) VALUES (?, ?, ?, ?)''',
              (userEmail, userCredentials, messageSubject, messageBody))

    conn.commit()
    conn.close()
