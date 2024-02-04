import uuid
import os
import sqlite3
from collections import defaultdict
from contextlib import contextmanager
import settings

@contextmanager
def get_cursor():
    try:
        conn = sqlite3.connect(settings.DB_PATH, timeout=30)
        yield conn, conn.cursor()
    finally:
        conn.close()

def setup_db():
    with get_cursor() as (conn, c):
        c.execute("CREATE TABLE IF NOT EXISTS hash (hash TEXT, offset REAL, song_id TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS song_info (artist TEXT, album TEXT, title TEXT, song_id TEXT)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON hash (hash)")
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA wal_autocheckpoint=300")

def checkpoint_db():
    with get_cursor() as (conn, c):
        c.execute("PRAGMA wal_checkpoint(FULL)")

def song_in_db(filename):
    with get_cursor() as (conn, c):
        song_id = str(uuid.uuid5(uuid.NAMESPACE_OID, filename).int)
        c.execute("SELECT * FROM song_info WHERE song_id=?", (song_id,))
        return c.fetchone() is not None

def store_song(hashes, song_info):
    with get_cursor() as (conn, c):
        c.execute('''
            CREATE TABLE IF NOT EXISTS song_info (
                artist TEXT,
                album TEXT,
                title TEXT,
                song_id TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS hash (
                hash TEXT,
                offset REAL,
                song_id TEXT
            )
        ''')
        title = os.path.splitext(os.path.basename(song_info[2]))[0]  # Extrahiere den Dateinamen als Titel
        c.execute("INSERT INTO song_info VALUES (?, ?, ?, ?)", (*song_info[:2], title, hashes[0][2]))
        c.executemany("INSERT INTO hash VALUES (?, ?, ?)", hashes)
        conn.commit()

def get_matches(hashes, threshold=5):
    h_dict = {}
    for h, t, _ in hashes:
        h_dict[str(h)] = t  # Änderung hier, da h bereits ein einzelnes Element ist

    in_values = f"({','.join([str(h[0]) for h in hashes])})"

    with get_cursor() as (conn, c):
        c.execute(f"SELECT hash, offset, song_id FROM hash WHERE hash IN {in_values}")
        results = c.fetchall()

    result_dict = defaultdict(list)
    for r in results:
        result_dict[r[2]].append((r[1], h_dict[str(r[0])]))  # Änderung hier

    return result_dict

def get_info_for_song_id(song_id):
    """Lookup song information for a given ID."""
    with get_cursor() as (conn, c):
        c.execute("SELECT title FROM song_info WHERE song_id = ?", (song_id,))
        result = c.fetchone()
        return result[0] if result else None
