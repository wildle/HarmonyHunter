from tinydb import TinyDB, Query
from tinydb.database import Table
from contextlib import contextmanager
from typing import Generator

class DatabaseManager:
    def __init__(self, db_path):
        """
        Initialisiert den DatabaseManager mit dem angegebenen Pfad zur Datenbank.

        Args:
            db_path (str): Der Pfad zur Datenbankdatei.
        """
        self.db = TinyDB(db_path)

    @contextmanager
    def get_cursor(self, table_name='_default') -> Generator[Table, None, None]:
        """
        Stellt einen Cursor für die angegebene Tabelle bereit.

        Args:
            table_name (str): Der Name der Tabelle. Standardmäßig '_default'.

        Yields:
            Table: Ein Cursor für die angegebene Tabelle.
        """
        table = self.db.table(table_name)
        yield table
        # Hier können nach Bedarf Bereinigungs- oder zusätzliche Operationen nach dem 'with'-Block durchgeführt werden

    def save_to_database(self, hashes, song_info):
        """
        Speichert Fingerabdrücke und Songinformationen in der Datenbank.

        Args:
            hashes (list): Eine Liste von Hashwerten.
            song_info (list): Eine Liste von Songinformationen (Künstler, Album, Titel).

        Returns:
            None
        """
        with self.get_cursor() as table:
            hash_entries = [{'hash': h[0], 'offset': h[1], 'song_id': h[2]} for h in hashes]

            song_id = hashes[0][2]
            insert_info = [i if i is not None else "Unknown" for i in song_info]
            song_info_entry = {'artist': insert_info[0], 'album': insert_info[1], 'title': insert_info[2], 'song_id': song_id}
            
            # Verwenden des 'table'-Objekts, das vom Kontext-Manager zurückgegeben wird
            table.insert(song_info_entry)
            table.insert_multiple(hash_entries)

    def get_title_from_song_id(self, song_id):
        """
        Holt den Titel eines Songs anhand seiner ID aus der Datenbank.

        Args:
            song_id (str): Die ID des Songs.

        Returns:
            str oder None: Der Titel des Songs oder None, wenn kein Eintrag gefunden wurde.
        """
        with self.get_cursor() as table:
            Song = Query()
            result = table.get(Song.song_id == song_id)
        return result['title'] if result and 'title' in result else None
