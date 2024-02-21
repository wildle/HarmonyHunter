import streamlit as st
from streamlit_option_menu import option_menu
from tinydb import TinyDB, Query
from fingerprints import Fingerprint
from recognise import RecognizeSong
from storage import DatabaseManager
from audio_recorder import record_audio
from audio_identifier import identify_recorded_music
from metadata import get_song_metadata

db = TinyDB('database.json')
db_manager = DatabaseManager('database.json')
fingerprint_instance = Fingerprint()
recognize_instance = RecognizeSong(db_manager)

def identify_music(uploaded_file):
    st.audio(uploaded_file)

    sample_fingerprints = fingerprint_instance.fingerprint_file(uploaded_file)
    matches = recognize_instance.get_matches(sample_fingerprints)

    best_match_result = recognize_instance.best_match(matches)
    if best_match_result:
        song_id = str(best_match_result)
        title = db_manager.get_title_from_song_id(song_id)
        if title:
            st.write("Musikstück:", title)
        else:
            st.warning("Titel nicht gefunden für Song ID: " + str(song_id))
    else:
        st.warning("Kein übereinstimmendes Musikstück gefunden.")

def main():
    st.title("HarmonyHunter")

    selected = option_menu(None, ["Musikstück einlernen", "Musikstück identifizieren"],
                           icons=['cloud', "settings"],
                           menu_icon="cast", default_index=0, orientation="horizontal")

    if selected == "Musikstück einlernen":
        st.subheader("Wähle eine Wav-Datei zum Einlernen aus")
        uploaded_file = st.file_uploader("Wav-Datei hochladen", type=["wav"])

        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/*', start_time=0)
            title = uploaded_file.name
            artist = "Artist"  
            album = "Album" 

            db_manager.save_to_database(fingerprint_instance.fingerprint_file(uploaded_file), (artist, album, title))
            st.success("Musikstück erfolgreich eingelernt.")

    elif selected == "Musikstück identifizieren":
        if st.button("Aufnahme starten"):
            st.write("Aufnahme gestartet...")
            record_audio('output.wav', duration=5)
            st.write("Aufnahme beendet!")

            st.write("Identifiziere Musikstück...")
            uploaded_file = open('output.wav', 'rb')
            title = identify_recorded_music(uploaded_file)
            st.write(title)

            artist, album, year = get_song_metadata(title)
            if artist and album and year:
                st.write(f"artist: {artist}")
                st.write(f"Album: {album}")
                st.write(f"Erscheinungsjahr: {year}")
            else:
                st.warning("Metadaten konnten nicht gefunden werden.")
            
        st.subheader("Wähle eine Wav-Datei zum Identifizieren aus")

        uploaded_file_identify = st.file_uploader("Wav-Datei hochladen", type=["wav"])

        if uploaded_file_identify is not None:
            identify_music(uploaded_file_identify)

if __name__ == "__main__":
    main()
