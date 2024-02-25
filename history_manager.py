from tinydb import TinyDB, Query

class HistoryManager:
    def __init__(self, db_path='database.json'):
        self.db = TinyDB(db_path)
        self.history_table = self.db.table('history')

    def add_to_history(self, song_id, title):
        self.history_table.insert({'song_id': song_id, 'title': title})

    def get_history(self):
        return self.history_table.all()