import streamlit as st
from streamlit_option_menu import option_menu
from tinydb import TinyDB, Query
import numpy as np
import uuid
import settings
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter
import json
import io
import os
from contextlib import contextmanager
from collections import defaultdict
import settings

db = TinyDB('database.json')

@contextmanager
def get_cursor():
    try:
        yield db.table('_default')
    finally:
        pass

def my_spectrogram(audio):
    nperseg = int(settings.SAMPLE_RATE * settings.FFT_WINDOW_SIZE)
    return spectrogram(audio, settings.SAMPLE_RATE, nperseg=nperseg)


def file_to_spectrogram(uploaded_file):

    audio_content = uploaded_file.read()
    a = AudioSegment.from_wav(io.BytesIO(audio_content)).set_channels(1).set_frame_rate(settings.SAMPLE_RATE)
    audio = np.frombuffer(a.raw_data, np.int16)
    return my_spectrogram(audio)


def find_peaks(Sxx):
    data_max = maximum_filter(Sxx, size=settings.PEAK_BOX_SIZE, mode='constant', cval=0.0)
    peak_goodmask = (Sxx == data_max)

    non_zero_indices = np.nonzero(peak_goodmask)

    if len(non_zero_indices) == 2:
        y_peaks, x_peaks = non_zero_indices
    else:
        y_peaks = non_zero_indices
        x_peaks = np.arange(len(y_peaks))

    if isinstance(y_peaks, np.ndarray) and isinstance(x_peaks, np.ndarray) and len(y_peaks) > 0 and len(x_peaks) > 0:
        peak_values = Sxx[y_peaks, x_peaks]
        i = peak_values.argsort()[::-1]
        j = [(y_peaks[idx], x_peaks[idx]) for idx in i]
        
        total = Sxx.shape[0] * Sxx.shape[1]
        peak_target = int((total / (settings.PEAK_BOX_SIZE**2)) * settings.POINT_EFFICIENCY)

        return j[:peak_target]
    else:
        print("Error: Unable to find valid peak values.")
        return []


def idxs_to_tf_pairs(idxs, t, f):
    return np.array([(f[i[0]], t[i[1]]) for i in idxs])


def hash_point_pair(p1, p2):
    return hash((p1[0], p2[0], p2[1]-p2[1]))


def target_zone(anchor, points, width, height, t):
    x_min = anchor[1] + t
    x_max = x_min + width
    y_min = anchor[0] - (height*0.5)
    y_max = y_min + height
    for point in points:
        if point[0] < y_min or point[0] > y_max:
            continue
        if point[1] < x_min or point[1] > x_max:
            continue
        yield point


def hash_points(points, filename):

    hashes = []
    song_id = uuid.uuid5(uuid.NAMESPACE_OID, str(filename)).int
    for anchor in points:
        for target in target_zone(
            anchor, points, settings.TARGET_T, settings.TARGET_F, settings.TARGET_START
        ):
            hashes.append((
                # hash
                hash_point_pair(anchor, target),
                # time offset
                anchor[1],
                # filename
                str(song_id)
            ))
    return hashes


def fingerprint_file(filename):

    f, t, Sxx = file_to_spectrogram(filename)
    peaks = find_peaks(Sxx)
    peaks = idxs_to_tf_pairs(peaks, t, f)
    return hash_points(peaks, filename)

def get_matches(hashes, threshold=5):
    h_dict = {h[0]: h[1] for h in hashes}
    in_values = list(h_dict.keys())

    with get_cursor() as table:
        results = table.search(Query().hash.one_of(in_values))

    result_dict = defaultdict(list)
    for r in results:
        if 'offset' in r:
            result_dict[r['song_id']].append((r['offset'], h_dict[r['hash']]))

    return result_dict

def score_match(offsets):
    binwidth = 0.5
    tks = list(map(lambda x: x[0] - x[1], offsets))
    hist, _ = np.histogram(tks,
                           bins=np.arange(int(min(tks)),
                                          int(max(tks)) + binwidth + 1,
                                          binwidth))
    return np.max(hist)

def best_match(matches):

    matched_song = None
    best_score = 0
    for song_id, offsets in matches.items():
        if len(offsets) < best_score:
            # can't be best score, avoid expensive histogram
            continue
        score = score_match(offsets)
        if score > best_score:
            best_score = score
            matched_song = song_id
    return matched_song

def save_to_database(hashes, song_info):

    hash_entries = [{'hash': h[0], 'offset': h[1], 'song_id': h[2]} for h in hashes]

    song_id = hashes[0][2]
    insert_info = [i if i is not None else "Unknown" for i in song_info]
    song_info_entry = {'artist': insert_info[0], 'album': insert_info[1], 'title': insert_info[2], 'song_id': song_id}
    db.table('_default').insert(song_info_entry)

    db.table('_default').insert_multiple(hash_entries)


def get_title_from_song_id(song_id):
    db_connector = TinyDB('database.json')
    Song = Query()
    result = db_connector.table('_default').get(Song.song_id == song_id)
    return result['title'] if result and 'title' in result else None

def identify_music(uploaded_file):
    st.audio(uploaded_file)

    sample_fingerprints = fingerprint_file(uploaded_file)
    matches = get_matches(sample_fingerprints)

    best_match_result = best_match(matches)
    if best_match_result:
        song_id = str(best_match_result)
        title = get_title_from_song_id(song_id)
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

            save_to_database(fingerprint_file(uploaded_file), (artist, album, title))
            st.success("Musikstück erfolgreich eingelernt.")

    elif selected == "Musikstück identifizieren":
        st.subheader("Wähle eine Wav-Datei zum Identifizieren aus")
        uploaded_file_identify = st.file_uploader("Wav-Datei hochladen", type=["wav"])

        if uploaded_file_identify is not None:
            identify_music(uploaded_file_identify)



if __name__ == "__main__":
    main()