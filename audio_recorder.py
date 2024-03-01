import pyaudio
import wave

def record_audio(filename, duration=5):
    """
    Nimmt Audio für eine bestimmte Dauer auf und speichert es als WAV-Datei.

    Args:
        filename (str): Der Name der WAV-Datei, in die das aufgenommene Audio gespeichert werden soll.
        duration (int): Die Dauer der Aufnahme in Sekunden. Standardmäßig 5 Sekunden.

    Returns:
        None
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* Aufnahme gestartet")

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Aufnahme beendet")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"* Audio wurde gespeichert als {filename}")
