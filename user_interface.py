import streamlit as st
import time
from streamlit_option_menu import option_menu
from tinydb import TinyDB, Query
from fingerprints import Fingerprint
from recognise import RecognizeSong
from storage import DatabaseManager
from audio_recorder import record_audio
from audio_identifier import identify_recorded_music
from album_cover import get_album_cover
from youtube_link import get_youtube_link
from apple_music_link import get_apple_music_link
from spotify_link import get_spotify_link
from history_manager import HistoryManager

db = TinyDB('database.json')
db_manager = DatabaseManager('database.json')
fingerprint_instance = Fingerprint()
recognize_instance = RecognizeSong(db_manager)
history_manager= HistoryManager('database.json')

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
            history_manager.add_to_history(song_id, title)
        else:
            st.warning("Titel nicht gefunden für Song ID: " + str(song_id))
    else:
        st.warning("Kein übereinstimmendes Musikstück gefunden.")
    

def main():
    st.title("HarmonyHunter")

    selected = option_menu(None, ["Musikstück einlernen", "Musikstück identifizieren", "Historie"],
                           icons=['cloud', "settings"],
                           menu_icon="cast", default_index=0, orientation="horizontal")
    

    if selected == "Musikstück einlernen":
        st.subheader("Wähle eine Wav-Datei zum Einlernen aus")
        uploaded_file = st.file_uploader("Wav-Datei hochladen", type=["wav"])

        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/*', start_time=0)
            title = st.text_input("Titel", "")
            artist = st.text_input("Interpret", "")
            album = st.text_input("Album", "")

            # Messen der Einlernzeit
            start_time_learning = time.time()
            db_manager.save_to_database(fingerprint_instance.fingerprint_file(uploaded_file), (artist, album, title))
            end_time_learning = time.time()
            duration_learning = end_time_learning - start_time_learning
            st.success(f"Musikstück erfolgreich eingelernt. Dauer: {duration_learning:.2f} Sekunden")


    elif selected == "Musikstück identifizieren":
        if st.button("Aufnahme starten"):
            st.write("Aufnahme gestartet...")
            record_audio('output.wav', duration=5)
            st.write("Aufnahme beendet!")

            # Messen der Identifizierungszeit
            start_time_identification = time.time()
            st.write("Identifiziere Musikstück...")
            uploaded_file = open('output.wav', 'rb')
            title = identify_recorded_music(uploaded_file)
            end_time_identification = time.time()
            duration_identification = end_time_identification - start_time_identification
            st.write(f"Identifizierungsdauer: {duration_identification:.2f} Sekunden")

            # Wenn ein Titel identifiziert wurde
            if title:
                col1, col2, col3 = st.columns([1,3,1])

                with col1:
                    # Albumcover ausgeben
                    cover_url = get_album_cover(title)
                    if cover_url:
                        st.image(cover_url, width=100)
                    else:
                        st.warning("Albumcover nicht gefunden.")

                with col2:
                    st.write(title)

                with col3:
                    # YouTube-Link
                    youtube_link = get_youtube_link(title)
                    if youtube_link:
                        st.markdown(f"[YouTube]({youtube_link})")

                    # Apple Music-Link
                    apple_music_link = get_apple_music_link(title)
                    if apple_music_link:
                        st.markdown(f"[Apple Music]({apple_music_link})")

                    # Spotify-Link
                    spotify_link = get_spotify_link(title)
                    if spotify_link:
                        st.markdown(f"[Spotify]({spotify_link})")

                    if not youtube_link and not spotify_link and not apple_music_link:
                        st.warning("Keine Links gefunden.")
            else:
                st.warning("Kein übereinstimmendes Musikstück gefunden.")

        st.subheader("Wähle eine Wav-Datei zum Identifizieren aus")

        uploaded_file_identify = st.file_uploader("Wav-Datei hochladen", type=["wav"], key="unique_key")

        if uploaded_file_identify is not None:
            title = identify_music(uploaded_file_identify)

            # Wenn ein Titel identifiziert wurde
            if title:
                col1, col2, col3 = st.columns([1,3,1])

                with col1:
                    # Albumcover ausgeben
                    cover_url = get_album_cover(title)
                    if cover_url:
                        st.image(cover_url, caption='Albumcover', width=100)
                    else:
                        st.warning("Albumcover nicht gefunden.")

                with col2:
                    st.write(title)

                with col3:
                    # YouTube-Link
                    youtube_link = get_youtube_link(title)
                    if youtube_link:
                        st.markdown(f"[YouTube]({youtube_link})")

                    # Apple Music-Link
                    apple_music_link = get_apple_music_link(title)
                    if apple_music_link:
                        st.markdown(f"[Apple Music]({apple_music_link})")

                    # Spotify-Link
                    spotify_link = get_spotify_link(title)
                    if spotify_link:
                        st.markdown(f"[Spotify]({spotify_link})")

                    if not youtube_link and not spotify_link and not apple_music_link:
                        st.warning("Keine Links gefunden.")
            else:
                st.warning("Kein übereinstimmendes Musikstück gefunden.")

    elif selected == "Historie":
        st.subheader("Historie der erkannten Musikstücke")
        history = history_manager.get_history()
        for song in history:
            col1, col2, col3 = st.columns([1,3,1])

            with col1:
                # Albumcover ausgeben
                cover_url = get_album_cover(song['title'])
                if cover_url:
                    st.image(cover_url, width=100)
                else:
                    st.warning("Albumcover nicht gefunden.")

            with col2:
                st.write(f"Titel: {song['title']}")
                st.write(f"Datum \\& Zeit: {song['time']}")

            with col3:
                # YouTube-Link
                youtube_link = get_youtube_link(song['title'])
                if youtube_link:
                    st.markdown(f"[YouTube]({youtube_link})")

                # Apple Music-Link
                apple_music_link = get_apple_music_link(song['title'])
                if apple_music_link:
                    st.markdown(f"[Apple Music]({apple_music_link})")

                # Spotify-Link
                spotify_link = get_spotify_link(song['title'])
                if spotify_link:
                    st.markdown(f"[Spotify]({spotify_link})")

                if not youtube_link and not spotify_link and not apple_music_link:
                    st.warning("Keine Links gefunden.")

if __name__ == "__main__":
    main()
