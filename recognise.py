import numpy as np
from tinydb import TinyDB, Query
from collections import defaultdict

class RecognizeSong:
    """
    Diese Klasse dient der Erkennung von Songs anhand ihrer Fingerabdrücke.
    """

    def __init__(self, db_manager):
        """
        Initialisiert die RecognizeSong-Klasse.

        Args:
            db_manager: Eine Instanz des DatabaseManagers.
        """
        self.db_manager = db_manager

    def get_matches(self, hashes, threshold=5):
        """
        Sucht in der Datenbank nach Fingerabdruckübereinstimmungen.

        Args:
            hashes: Eine Liste von Hashwerten.
            threshold (int): Schwellenwert für die Übereinstimmung. Standardmäßig 5.

        Returns:
            defaultdict: Ein Dictionary mit Song-IDs als Schlüssel und den entsprechenden Übereinstimmungen als Werte.
        """
        # Erstellen eines Hash-Dictionarys aus der Liste der Hashwerte
        h_dict = {h[0]: h[1] for h in hashes}
        in_values = list(h_dict.keys())

        # Suche nach Übereinstimmungen in der Datenbank
        with self.db_manager.get_cursor() as table:
            results = table.search(Query().hash.one_of(in_values))

        # Ergebnisse in ein defaultdict gruppieren
        result_dict = defaultdict(list)
        for r in results:
            if 'offset' in r:
                result_dict[r['song_id']].append((r['offset'], h_dict[r['hash']]))

        return result_dict

    def score_match(self, offsets):
        """
        Bewertet eine Übereinstimmung basierend auf den Zeitoffsets.

        Args:
            offsets: Eine Liste von Zeitoffsets.

        Returns:
            int: Die Bewertung der Übereinstimmung.
        """
        binwidth = 0.5
        tks = list(map(lambda x: x[0] - x[1], offsets))
        hist, _ = np.histogram(tks,
                               bins=np.arange(int(min(tks)),
                                              int(max(tks)) + binwidth + 1,
                                              binwidth))
        return np.max(hist)

    def best_match(self, matches):
        """
        Ermittelt die beste Übereinstimmung aus einer Liste von Übereinstimmungen.

        Args:
            matches: Ein Dictionary von Übereinstimmungen.

        Returns:
            str oder None: Die Song-ID der besten Übereinstimmung oder None, wenn keine gefunden wurde.
        """
        matched_song = None
        best_score = 0
        for song_id, offsets in matches.items():
            if len(offsets) < best_score:
                # Kann nicht die beste Übereinstimmung sein, teure Histogramme vermeiden
                continue
            score = self.score_match(offsets)
            if score > best_score:
                best_score = score
                matched_song = song_id
        return matched_song
