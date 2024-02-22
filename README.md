# HarmonyHunter

HarmonyHunter is a music recognition system built with Python. It uses audio fingerprinting techniques to identify music from audio files.

## Features

- Audio fingerprinting and storage
- Music recognition from audio files
- Interactive user interface

## Dependencies

The project depends on several Python libraries including:

- `numpy`
- `scikit-learn`
- `matplotlib`
- `jupyter`
- `PyAudio`
- `pydub`
- `tinytag`
- `streamlit`
- `tinydb`

You can install these dependencies using pip:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

The application provides an interactive user interface for learning and identifying music pieces. You can run the application using the following command:

\`\`\`bash
streamlit run user_interface.py
\`\`\`

In the application, you can choose to either learn a new music piece or identify a music piece.

- To learn a new music piece, select "Musikstück einlernen", upload a .wav file, and the application will fingerprint the audio and store it in the database.

- To identify a music piece, select "Musikstück identifizieren", upload a .wav file, and the application will fingerprint the audio and search the database for a match.

## Project Structure

The project consists of several Python files:

- `settings.py`: Contains global settings for the project.
- `storage.py`: Defines the `DatabaseManager` class for interacting with the TinyDB database.
- `user_interface.py`: Contains the Streamlit application for the user interface.
- `fingerprints.py` : Finds peaks, creates hashes and fingerprints. 
- `recognize.py` : Finds matches.
- `audio_recorder.py` : Records audio.
- `audio_identifier.py` : Identifies audio.
- `album_cover.py` : Finds album covers with Duckduckgo.
- `youtube_link.py` : Finds Youtube links with Duckduckgo.

## Add-ons
- Recording via microphone
- Determine and display the album cover of the music track
- Benchmarking the application: How long does the teach-in process take? How long does identification take?
- Link to identified piece of music on YouTube
- History of the last identified pieces of music????


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.