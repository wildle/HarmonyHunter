from fingerprints import Fingerprint
from recognise import RecognizeSong
from storage import DatabaseManager
from history_manager import HistoryManager  # Import der HistoryManager-Klasse

# Initialisierung der Klasseninstanzen
db_manager = DatabaseManager('database.json')
fingerprint_instance = Fingerprint()
recognize_instance = RecognizeSong(db_manager)
history_manager = HistoryManager('database.json')  # Instanzierung der HistoryManager-Klasse

def identify_music(uploaded_file):
    """
    Identifiziert die hochgeladene Musikdatei.

    Args:
        uploaded_file: Die hochgeladene Musikdatei.

    Returns:
        str oder None: Der Titel des identifizierten Songs oder None, wenn kein Match gefunden wurde.
    """
    # Erstellen von Fingerabdrücken aus der hochgeladenen Datei
    sample_fingerprints = fingerprint_instance.fingerprint_file(uploaded_file)
    
    # Vergleichen der Fingerabdrücke mit der Datenbank
    matches = recognize_instance.get_matches(sample_fingerprints)
    
    # Ermitteln der besten Übereinstimmung
    best_match_result = recognize_instance.best_match(matches)
    
    # Wenn eine Übereinstimmung gefunden wurde
    if best_match_result:
        # Holen des Titels des Songs basierend auf der besten Übereinstimmung
        song_id = str(best_match_result)
        title = db_manager.get_title_from_song_id(song_id)
        # Hinzufügen des identifizierten Songs zur Historie
        history_manager.add_to_history(str(best_match_result), title)

        return title
    
    # Wenn keine Übereinstimmung gefunden wurde
    return None
