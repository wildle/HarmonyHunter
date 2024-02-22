from fingerprints import Fingerprint
from recognise import RecognizeSong
from storage import DatabaseManager

def identify_recorded_music(uploaded_file):
    # Erzeuge Instanzen der benötigten Klassen
    db_manager = DatabaseManager('database.json')
    fingerprint_instance = Fingerprint()
    recognize_instance = RecognizeSong(db_manager)

    # Erzeuge Fingerabdrücke aus der aufgenommenen Audiodatei
    sample_fingerprints = fingerprint_instance.fingerprint_file(uploaded_file)

    # Suche nach Übereinstimmungen in der Datenbank
    matches = recognize_instance.get_matches(sample_fingerprints)

    # Bestimme das beste Übereinstimmungsergebnis
    best_match_result = recognize_instance.best_match(matches)

    # Gib das Ergebnis aus
    if best_match_result:
        song_id = str(best_match_result)
        title = db_manager.get_title_from_song_id(song_id)
        if title:
            return title
        else:
            return "Titel nicht gefunden für Song ID: " + str(song_id)
    else:
        return None
