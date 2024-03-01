from datetime import datetime
from tinydb import TinyDB, Query

class HistoryManager:
    """
    Diese Klasse verwaltet die Historie von erkannten Songs.
    """

    def __init__(self, db_path='history.json'):
        """
        Initialisiert die HistoryManager-Klasse.

        Args:
            db_path (str): Der Pfad zur Datenbankdatei. Standardmäßig 'history.json'.
        """
        self.db = TinyDB(db_path)
        self.history_table = self.db.table('history')

    def add_to_history(self, song_id, title):
        """
        Fügt einen erkannten Song zur Historie hinzu.

        Args:
            song_id (str): Die eindeutige ID des erkannten Songs.
            title (str): Der Titel des erkannten Songs.

        Returns:
            None
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_table.insert({'time': current_time, 'title': title})

    def get_history(self):
        """
        Ruft die gesamte Historie von erkannten Songs ab.

        Returns:
            list: Eine Liste von Dictionaries, die Informationen über erkannte Songs enthalten.
        """
        return self.history_table.all()
