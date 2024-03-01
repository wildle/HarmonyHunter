from fingerprints import Fingerprint
from recognise import RecognizeSong
from storage import DatabaseManager

# Hier die Klasseninstanzen initialisieren
db_manager = DatabaseManager('database.json')
fingerprint_instance = Fingerprint()
recognize_instance = RecognizeSong(db_manager)

def identify_music(uploaded_file):
    sample_fingerprints = fingerprint_instance.fingerprint_file(uploaded_file)
    matches = recognize_instance.get_matches(sample_fingerprints)
    best_match_result = recognize_instance.best_match(matches)
    if best_match_result:
        return db_manager.get_title_from_song_id(str(best_match_result))
    return None
