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
from music_identifier import identify_music
from registrierung import Registrierung
import os

# Datenbank-Initialisierung
db = TinyDB('database.json')
db_manager = DatabaseManager('database.json')
fingerprint_instance = Fingerprint()
recognize_instance = RecognizeSong(db_manager)
history_manager = HistoryManager('database.json')

def got_to_state_registrierung():
    st.session_state["state"] = "registrierung"

def got_to_state_login():
    st.session_state["state"] = "login"

def got_to_state_eingeloggt():
    st.session_state["state"] = "eingeloggt"

def main():
    """
    Hauptfunktion für die Streamlit-Anwendung "HarmonyHunter".
    """

    if "state" not in st.session_state:
            st.header("HarmonyHunter")

            st.button("Registrierung",on_click=got_to_state_registrierung)

            st.button("Login", on_click=got_to_state_login)


    elif st.session_state["state"] == "registrierung":
            st.header("Registrierung")
            
            registrierung_username = st.text_input("Name")
            registrierung_email = st.text_input("email")
            registrierung_password = st.text_input("Password", type="password")
            
                
            if st.button("speichern"):
                new_registrierung = Registrierung(registrierung_username, registrierung_email, registrierung_password)
                new_registrierung.store()
                st.success("Registrierung successful!")
                st.button("Login", on_click=got_to_state_login)
               
 
    elif st.session_state["state"] == "login":
            st.header("Login")
            login_name = st.text_input("Name")
            login_password = st.text_input("Password", type="password")
            

            if st.button("Login"):
                user_query = (Query().username == login_name) & (Query().password == login_password)
                user_data = Registrierung.get_db_connector().search(user_query)

                if user_data:
                    st.success("Login successful!")
                    # Additional button for further actions
                    st.button("weiter", on_click=got_to_state_eingeloggt)
                        # Set the login state or perform other actions here
                else:
                    st.error("Invalid username or password.")
                    


    elif st.session_state["state"] == "eingeloggt":

        st.title("HarmonyHunter")

        # Auswahl des Menüs
        selected = option_menu(None, ["Musikstück einlernen", "Musikstück identifizieren", "Historie"],
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

                # Messen der Einlernzeit
                start_time_learning = time.time()
                db_manager.save_to_database(fingerprint_instance.fingerprint_file(uploaded_file), (artist, album, title))
                end_time_learning = time.time()
                duration_learning = end_time_learning - start_time_learning
                st.success(f"Musikstück erfolgreich eingelernt. Dauer: {duration_learning:.2f} Sekunden")


        elif selected == "Musikstück identifizieren":
            title = None  # Initialisierung von 'title'
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
                        base_name, extension = os.path.splitext(title)
                        st.write(base_name)

                    with col3:
                        # YouTube-Link
                        youtube_link = get_youtube_link(title)
                        apple_music_link = get_apple_music_link(title)
                        spotify_link = get_spotify_link(title)

                        if youtube_link:
                            st.markdown(f"[YouTube]({youtube_link})")
                        else:
                            st.warning("YouTube-Link nicht gefunden.")

                        if apple_music_link:
                            st.markdown(f"[Apple Music]({apple_music_link})")
                        else:
                            st.warning("Apple Music-Link nicht gefunden.")

                        if spotify_link:
                            st.markdown(f"[Spotify]({spotify_link})")
                        else:
                            st.warning("Spotify-Link nicht gefunden.")

            st.subheader("Wähle eine Wav-Datei zum Identifizieren aus")

            uploaded_file_identify = st.file_uploader("Wav-Datei hochladen", type=["wav"], key="unique_key")

            if uploaded_file_identify is not None:
                # Eindeutiger Schlüssel für den Button basierend auf der Datei hochladen
                button_key = f"button_{uploaded_file_identify.name}"
                if st.button("Musikstück erkennen", key=button_key):
                    title = identify_music(uploaded_file_identify)
            
                st.divider()

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
                        base_name, extension = os.path.splitext(title)
                        st.write(f"Titel: {base_name}")
                    with col3:
                        # YouTube-Link
                        youtube_link = get_youtube_link(title)
                        apple_music_link = get_apple_music_link(title)
                        spotify_link = get_spotify_link(title)

                        if youtube_link:
                            st.markdown(f"[YouTube]({youtube_link})")
                        else:
                            st.warning("YouTube-Link nicht gefunden.")

                        if apple_music_link:
                            st.markdown(f"[Apple Music]({apple_music_link})")
                        else:
                            st.warning("Apple Music-Link nicht gefunden.")

                        if spotify_link:
                            st.markdown(f"[Spotify]({spotify_link})")
                        else:
                            st.warning("Spotify-Link nicht gefunden.")


        elif selected == "Historie":
            st.subheader("Historie der erkannten Musikstücke")
            history = history_manager.get_history()[::-1]  # Umkehrung der Reihenfolge für die neuesten Einträge zuerst
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
                    base_name, extension = os.path.splitext(song['title'])
                    st.write(f"Titel: {base_name}")  # Anpassung hier
                    st.write(f"Datum & Zeit: {song['time']}")

                with col3:
                    # YouTube-Link
                    youtube_link = get_youtube_link(song['title'])
                    apple_music_link = get_apple_music_link(song['title'])
                    spotify_link = get_spotify_link(song['title'])

                    links_found = False
                    if youtube_link:
                        st.markdown(f"[YouTube]({youtube_link})")
                        links_found = True

                    if apple_music_link:
                        st.markdown(f"[Apple Music]({apple_music_link})")
                        links_found = True

                    if spotify_link:
                        st.markdown(f"[Spotify]({spotify_link})")
                        links_found = True

                    if not links_found:
                        st.warning("Keine Links gefunden.")

if __name__ == "__main__":
    main()
