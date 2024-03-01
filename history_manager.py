from datetime import datetime
from tinydb import TinyDB, Query

class HistoryManager:
    def __init__(self, db_path='database.json'):
        self.db = TinyDB(db_path)
        self.history_table = self.db.table('history')

    def add_to_history(self, song_id, title):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_table.insert({'time': current_time, 'title': title})

    def get_history(self):
        return self.history_table.all()