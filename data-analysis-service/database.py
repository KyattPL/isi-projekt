import sqlite3


def create_snapshot_table():
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute("...")

    conn.commit()
    conn.close()


def create_matches_table():
    # Creates a new database file if it doesn't exist
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS MATCHES
                 (id INTEGER PRIMARY KEY, snapshotId INTEGER, patch TEXT,
                 gameDuration INTEGER, championName TEXT, kills INTEGER, deaths INTEGER,
                 assists INTEGER, champExperience INTEGER, goldEarned INTEGER, totalDamageDealtToChampions INTEGER,
                 totalDamageTaken INTEGER, totalHeal INTEGER, totalMinionsKilled INTEGER),
                 visionScore INTEGER, was_won INTEGER
              ''')

    conn.commit()
    conn.close()


def insert_match(snapshotId, patch, gameDuration, championName, kills, deaths, assists, champExperience,
                 goldEarned, totalDamageDealtToChampions, totalDamageTaken, totalHeal, totalMinionsKilled, visionScore, was_won):
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute("INSERT INTO MATCHES (snapshotId, patch, gameDuration, championName, kills, deaths, assists, \
              champExperience, goldEarned, totalDamageDealtToChampions, totalDamageTaken, totalHeal, \
              totalMinionsKilled, visionScore, was_won) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (snapshotId, patch, gameDuration, championName, kills, deaths, assists, champExperience, goldEarned,
               totalDamageDealtToChampions, totalDamageTaken, totalHeal, totalMinionsKilled, visionScore, was_won))

    conn.commit()
    conn.close()


def get_matches():
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute("SELECT * FROM MATCHES")

    matches = c.fetchall()
    conn.close()

    return matches
