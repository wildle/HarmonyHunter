import numpy as np
from tinydb import TinyDB, Query
from collections import defaultdict

class RecognizeSong:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_matches(self, hashes, threshold=5):
        h_dict = {h[0]: h[1] for h in hashes}
        in_values = list(h_dict.keys())

        with self.db_manager.get_cursor() as table:
            results = table.search(Query().hash.one_of(in_values))


        result_dict = defaultdict(list)
        for r in results:
            if 'offset' in r:
                result_dict[r['song_id']].append((r['offset'], h_dict[r['hash']]))

        return result_dict

    def score_match(self, offsets):
        binwidth = 0.5
        tks = list(map(lambda x: x[0] - x[1], offsets))
        hist, _ = np.histogram(tks,
                            bins=np.arange(int(min(tks)),
                                            int(max(tks)) + binwidth + 1,
                                            binwidth))
        return np.max(hist)

    def best_match(self, matches):
        matched_song = None
        best_score = 0
        for song_id, offsets in matches.items():
            if len(offsets) < best_score:
                # can't be the best score, avoid expensive histogram
                continue
            score = self.score_match(offsets)
            if score > best_score:
                best_score = score
                matched_song = song_id
        return matched_song
