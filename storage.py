from tinydb import TinyDB, Query
from tinydb.database import Table
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path):
        self.db = TinyDB(db_path)

    @contextmanager
    def get_cursor(self, table_name='_default') -> Table:
        table = self.db.table(table_name)
        yield table
        # You can perform any cleanup or additional operations after the 'with' block if needed

    def save_to_database(self, hashes, song_info):
        with self.get_cursor() as table:
            hash_entries = [{'hash': h[0], 'offset': h[1], 'song_id': h[2]} for h in hashes]

            song_id = hashes[0][2]
            insert_info = [i if i is not None else "Unknown" for i in song_info]
            song_info_entry = {'artist': insert_info[0], 'album': insert_info[1], 'title': insert_info[2], 'song_id': song_id}
            
            # Use the 'table' object returned by the context manager
            table.insert(song_info_entry)
            table.insert_multiple(hash_entries)

    def get_title_from_song_id(self, song_id):
        with self.get_cursor() as table:
            Song = Query()
            result = table.get(Song.song_id == song_id)
        return result['title'] if result and 'title' in result else None
