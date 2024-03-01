from fingerprints import Fingerprint
from recognise import RecognizeSong
from storage import DatabaseManager
from history_manager import HistoryManager

# Hier die Klasseninstanzen initialisieren
db_manager = DatabaseManager('database.json')
fingerprint_instance = Fingerprint()
recognize_instance = RecognizeSong(db_manager)
history_manager = HistoryManager('history.json')  # Instanzierung der HistoryManager-Klasse

def identify_music(uploaded_file):
    sample_fingerprints = fingerprint_instance.fingerprint_file(uploaded_file)
    matches = recognize_instance.get_matches(sample_fingerprints)
    best_match_result = recognize_instance.best_match(matches)
    if best_match_result:
        # Holen des Titels des Songs basierend auf der besten Übereinstimmung
        title = db_manager.get_title_from_song_id(str(best_match_result))
        
        # Überprüfen, ob best_match_result nicht None ist
        if title:
            # Hinzufügen des identifizierten Songs zur Historie
            history_manager.add_to_history(str(best_match_result), title)
        else:
            print("Titel nicht gefunden.")
        
        return title
    return None
