import sqlite3


def create_snapshot_table():
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS SNAPSHOT
              (champion TEXT PRIMARY KEY, killsAvg REAL, deathsAvg REAL, assistsAvg REAL, expAvg REAL,
              goldAvg REAL, damageDealtAvg REAL, damageTakenAvg REAL, healAvg REAL, csAvg REAL, visionScoreAvg REAL)''')

    conn.commit()
    conn.close()


def insert_snapshot(champion, killsAvg, deathsAvg, assistsAvg, expAvg, goldAvg, damageDealtAvg,
                    damageTakenAvg, healAvg, csAvg, visionScoreAvg):
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute('''INSERT INTO SNAPSHOT (champion, killsAvg, deathsAvg, assistsAvg, expAvg,
              goldAvg, damageDealtAvg, damageTakenAvg, healAvg, csAvg, visionScoreAvg) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (champion, killsAvg, deathsAvg, assistsAvg, expAvg, goldAvg, damageDealtAvg,
               damageTakenAvg, healAvg, csAvg, visionScoreAvg))

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
                 totalDamageTaken INTEGER, totalHeal INTEGER, totalMinionsKilled INTEGER,
                 visionScore INTEGER, was_won INTEGER)
              ''')

    conn.commit()
    conn.close()


def insert_match(snapshotId, patch, gameDuration, championName, kills, deaths, assists, champExperience,
                 goldEarned, totalDamageDealtToChampions, totalDamageTaken, totalHeal, totalMinionsKilled, visionScore, was_won):
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute('''INSERT INTO MATCHES (snapshotId, patch, gameDuration, championName, kills, deaths, assists,
              champExperience, goldEarned, totalDamageDealtToChampions, totalDamageTaken, totalHeal,
              totalMinionsKilled, visionScore, was_won) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
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


def get_snapshot(snapshotId):
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM SNAPSHOT WHERE snapshotId = ?''', (snapshotId,))

    champAvgs = c.fetchall()
    conn.close()

    return champAvgs


def calculate_avg_per_champion(snapshotId):
    conn = sqlite3.connect('matches.db')
    c = conn.cursor()

    c.execute('''SELECT * FROM MATCHES WHERE snapshotId = ?''', (snapshotId,))
    matches = c.fetchall()

    champions_data = {}

    for match in matches:
        championName = match[4]
        gameDuration = match[3]

        # Initialize the champion's data if not already present
        if championName not in champions_data:
            champions_data[championName] = {
                'sum_kills': 0,
                'sum_deaths': 0,
                'sum_assists': 0,
                'sum_champExperience': 0,
                'sum_goldEarned': 0,
                'sum_totalDamageDealtToChampions': 0,
                'sum_totalDamageTaken': 0,
                'sum_totalHeal': 0,
                'sum_totalMinionsKilled': 0,
                'sum_visionScore': 0,
                'count': 0,
            }

        # Update the sum of each metric for the champion
        champions_data[championName]['sum_kills'] += match[5] / gameDuration
        champions_data[championName]['sum_deaths'] += match[6] / gameDuration
        champions_data[championName]['sum_assists'] += match[7] / gameDuration
        champions_data[championName]['sum_champExperience'] += match[8] / gameDuration
        champions_data[championName]['sum_goldEarned'] += match[9] / gameDuration
        champions_data[championName]['sum_totalDamageDealtToChampions'] += match[10] / gameDuration
        champions_data[championName]['sum_totalDamageTaken'] += match[11] / gameDuration
        champions_data[championName]['sum_totalHeal'] += match[12] / gameDuration
        champions_data[championName]['sum_totalMinionsKilled'] += match[13] / gameDuration
        champions_data[championName]['sum_visionScore'] += match[14] / gameDuration
        champions_data[championName]['count'] += 1

    # Calculate the average for each champion
    avg_per_champion = {}
    for champion, data in champions_data.items():
        avg_per_champion[champion] = {
            'avg_kills': data['sum_kills'] / data['count'],
            'avg_deaths': data['sum_deaths'] / data['count'],
            'avg_assists': data['sum_assists'] / data['count'],
            'avg_champExperience': data['sum_champExperience'] / data['count'],
            'avg_goldEarned': data['sum_goldEarned'] / data['count'],
            'avg_totalDamageDealtToChampions': data['sum_totalDamageDealtToChampions'] / data['count'],
            'avg_totalDamageTaken': data['sum_totalDamageTaken'] / data['count'],
            'avg_totalHeal': data['sum_totalHeal'] / data['count'],
            'avg_totalMinionsKilled': data['sum_totalMinionsKilled'] / data['count'],
            'avg_visionScore': data['sum_visionScore'] / data['count'],
        }

    conn.close()

    return avg_per_champion
