import os
import logging
from multiprocessing import Pool, Lock, current_process
import numpy as np
from tinytag import TinyTag
import settings
from fingerprint import fingerprint_file, fingerprint_audio
from storage import store_song, get_matches, get_info_for_song_id, song_in_db, checkpoint_db

KNOWN_EXTENSIONS = ["mp3", "wav", "flac", "m4a"]


def get_song_info(filename):
    """Gets the ID3 tags for a file. Returns None for tuple values that don't exist.

    :param filename: Path to the file with tags to read
    :returns: (artist, album, title)
    :rtype: tuple(str/None, str/None, str/None)
    """
    tag = TinyTag.get(filename)
    artist = tag.artist if tag.albumartist is None else tag.albumartist
    title = tag.title

    # If title is None or empty, extract it from the filename
    if not title:
        title = os.path.splitext(os.path.basename(filename))[0]

    return (artist, tag.album, title)


def register_song(filename):
    """Register a single song.

    Checks if the song is already registered based on path provided and ignores
    those that are already registered.

    :param filename: Path to the file to register"""
    if song_in_db(filename):
        return
    hashes = fingerprint_file(filename)
    song_info = get_song_info(filename)
    try:
        logging.info(f"{current_process().name} waiting to write {filename}")
        with lock:
            logging.info(f"{current_process().name} writing {filename}")
            store_song(hashes, song_info)
            logging.info(f"{current_process().name} wrote {filename}")
    except NameError:
        logging.info(f"Single-threaded write of {filename}")
        # running single-threaded, no lock needed
        store_song(hashes, song_info)


def register_directory(path):
    """Recursively register songs in a directory.

    Uses :data:`~abracadabra.settings.NUM_WORKERS` workers in a pool to register songs in a
    directory.

    :param path: Path of directory to register
    """
    def pool_init(l):
        """Init function that makes a lock available to each of the workers in
        the pool. Allows synchronisation of db writes since SQLite only supports
        one writer at a time.
        """
        global lock
        lock = l
        logging.info(f"Pool init in {current_process().name}")

    to_register = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.split('.')[-1] not in KNOWN_EXTENSIONS:
                continue
            file_path = os.path.join(path, root, f)
            to_register.append(file_path)
    l = Lock()
    with Pool(settings.NUM_WORKERS, initializer=pool_init, initargs=(l,)) as p:
        p.map(register_song, to_register)
    # speed up future reads
    checkpoint_db()


def score_match(offsets):
    """Score a matched song.

    Calculates a histogram of the deltas between the time offsets of the hashes from the
    recorded sample and the time offsets of the hashes matched in the database for a song.
    The function then returns the size of the largest bin in this histogram as a score.

    :param offsets: List of offset pairs for matching hashes
    :returns: The highest peak in a histogram of time deltas
    :rtype: int
    """
    # Use bins spaced 0.5 seconds apart
    binwidth = 0.5
    tks = list(map(lambda x: x[0] - x[1], offsets))
    hist, _ = np.histogram(tks,
                           bins=np.arange(int(min(tks)),
                                          int(max(tks)) + binwidth + 1,
                                          binwidth))
    return np.max(hist)


def best_match(matches):
    """Find the best match from the given matches.

    :param matches: A dictionary mapping ``song_id`` to a list of time offset tuples.
    :type matches: dict(str: list(tuple(float, float)))
    :returns: The best match information.
    :rtype: dict(str: list(tuple(float, float))) or None
    """
    best_song_id = None
    best_count = 0

    for song_id, offsets in matches.items():
        count = len(offsets)
        if count > best_count:
            best_count = count
            best_song_id = song_id

    if best_song_id:
        title = get_info_for_song_id(best_song_id)
        if title:
            return {'title': title, 'offsets': matches[best_song_id]}

    return None



def recognise_song(filename):
    """Recognises a pre-recorded sample.

    Recognises the sample stored at the path ``filename``. The sample can be in any of the
    formats in :data:`recognise.KNOWN_FORMATS`.

    :param filename: Path of file to be recognised.
    :returns: :func:`~abracadabra.recognise.get_song_info` result for matched song or None.
    :rtype: tuple(str, str, str)
    """
    hashes = fingerprint_file(filename)
    matches = get_matches(hashes)
    matched_song = best_match(matches)
    info = get_info_for_song_id(matched_song)
    if info is not None:
        return info
    return matched_song
