import streamlit as st
from fingerprint import fingerprint_file, fingerprint_audio, file_to_spectrogram, find_peaks, idxs_to_tf_pairs, hash_points
from recognise import get_info_for_song_id, get_matches, best_match, get_song_info
from storage import store_song, get_cursor
import tempfile
import os
import re
import struct
import sqlite3

def main():
    st.title("HarmonyHunter")

    tabs = ["Musikstücke einlernen", "Musikstück identifizieren"]
    choice = st.sidebar.selectbox("Choose a tab", tabs)

    if choice == "Musikstücke einlernen":
        learn_music_tab()
    elif choice == "Musikstück identifizieren":
        identify_music_tab()

def get_all_songs():
    with get_cursor() as (conn, c):
        try:
            c.execute("SELECT DISTINCT title FROM song_info")
            return [row[0] for row in c.fetchall()]
        except sqlite3.OperationalError as e:
            return []

def learn_music_tab():
    st.header("Musikstücke einlernen")

    uploaded_file = st.file_uploader("Upload a music file", type=["wav"])
    if uploaded_file:
        st.audio(uploaded_file, format='audio/*', start_time=0)

        if st.button("Einlernen"):
            # Erhalte den ursprünglichen Dateinamen
            original_filename = uploaded_file.name

            # Create a temporary file with the content of the uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(uploaded_file.read())

            # Get song info using the temporary file path
            fingerprints = fingerprint_file(temp_file.name)
            store_song(fingerprints, ("Artist", "Album", original_filename))

            # Do the rest of your processing with song_info...

            st.success("Musikstück erfolgreich eingelearned.")


def identify_music_tab():
    st.header("Musikstück identifizieren")

    all_songs = get_all_songs()
    if not all_songs:
        st.warning("Keine Musikstücke in der Datenbank gefunden.")
        return

    selected_song = st.selectbox("Wähle ein Musikstück", all_songs)

    with get_cursor() as (conn, c):
        c.execute("SELECT * FROM song_info WHERE title=?", (selected_song,))
        song_info = c.fetchone()

    if song_info:
        title = song_info[3] 
        with get_cursor() as (conn, c):
            c.execute("SELECT * FROM hash WHERE song_id=?", (title,))
            database_fingerprints = c.fetchall()
    else:
        st.warning("Song-ID für den ausgewählten Titel nicht gefunden.")
    

    if st.button("identifizieren"):
        # Match the fingerprints to identify the song
        matches = get_matches(database_fingerprints)

        # Find the best match
        best_match_result = best_match(matches)
        if best_match_result:
            st.write("Musikstück:", best_match_result['title'])
        else:
            st.warning("Kein übereinstimmendes Musikstück gefunden.")

    uploaded_file = st.file_uploader("Upload a music file for identification", type=["wav"])
    
    if uploaded_file:
        st.audio(uploaded_file, format='audio/*', start_time=0)

        if st.button("Identifizieren"):
            # Create a temporary file with the content of the uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(uploaded_file.read())

            # Get fingerprints for the uploaded file
            query_fingerprints = fingerprint_file(temp_file.name)

            

            # Match the fingerprints to identify the song
            matches = get_matches(query_fingerprints)

            # Find the best match
            best_match_result = best_match(matches)
            if best_match_result:
                st.write("Musikstück:", best_match_result['title'])
            else:
                st.warning("Kein übereinstimmendes Musikstück gefunden.")

if __name__ == "__main__":
    main()