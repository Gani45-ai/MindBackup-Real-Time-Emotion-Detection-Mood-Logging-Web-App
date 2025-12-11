import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path('mindbackup.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emotion TEXT,
        confidence REAL,
        filename TEXT,
        timestamp TEXT
    )
    ''')
    conn.commit()
    conn.close()

def add_memory(emotion, confidence, filename):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute('INSERT INTO memories (emotion, confidence, filename, timestamp) VALUES (?, ?, ?, ?)', (emotion, confidence, filename, ts))
    conn.commit()
    conn.close()

def get_counts_period(period):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if period == 'minute':
        cur.execute('SELECT emotion, COUNT(*) FROM memories WHERE timestamp >= datetime("now", "-1 minutes") GROUP BY emotion')
    elif period == 'hour':
        cur.execute('SELECT emotion, COUNT(*) FROM memories WHERE timestamp >= datetime("now", "-1 hours") GROUP BY emotion')
    elif period == 'day':
        cur.execute('SELECT emotion, COUNT(*) FROM memories WHERE timestamp >= datetime("now", "-1 days") GROUP BY emotion')
    elif period == 'week':
        cur.execute('SELECT emotion, COUNT(*) FROM memories WHERE timestamp >= datetime("now", "-7 days") GROUP BY emotion')
    elif period == 'month':
        cur.execute('SELECT emotion, COUNT(*) FROM memories WHERE timestamp >= datetime("now", "-30 days") GROUP BY emotion')
    else:
        cur.execute('SELECT emotion, COUNT(*) FROM memories GROUP BY emotion')
    rows = cur.fetchall()
    conn.close()
    return dict(rows)

if __name__ == '__main__':
    init_db()
    print('DB initialized:', DB_PATH.resolve())
