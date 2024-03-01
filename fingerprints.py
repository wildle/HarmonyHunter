import settings
import numpy as np
import uuid
import io
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter

class Fingerprint:
    """
    Diese Klasse enthält Methoden zum Erstellen von Fingerabdrücken aus Audiodateien.
    """

    def file_to_spectrogram(self, uploaded_file):
        """
        Erzeugt ein Spektrogramm aus einer hochgeladenen Audiodatei.

        Args:
            uploaded_file: Die hochgeladene Audiodatei.

        Returns:
            f, t, Sxx: Die Frequenzen, Zeiten und das Spektrogramm der Audiodatei.
        """
        audio_content = uploaded_file.read()
        a = AudioSegment.from_wav(io.BytesIO(audio_content)).set_channels(1).set_frame_rate(settings.SAMPLE_RATE)
        audio = np.frombuffer(a.raw_data, np.int16)
        return self.my_spectrogram(audio)

    def my_spectrogram(self, audio):
        """
        Berechnet das Spektrogramm einer Audiodatei.

        Args:
            audio: Die Audiodatei als Numpy-Array.

        Returns:
            f, t, Sxx: Die Frequenzen, Zeiten und das Spektrogramm der Audiodatei.
        """
        nperseg = int(settings.SAMPLE_RATE * settings.FFT_WINDOW_SIZE)
        return spectrogram(audio, settings.SAMPLE_RATE, nperseg=nperseg)

    def find_peaks(self, Sxx):
        """
        Findet Peaks im Spektrogramm.

        Args:
            Sxx: Das Spektrogramm.

        Returns:
            Eine Liste von Peaks.
        """
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

    def idxs_to_tf_pairs(self, idxs, t, f):
        """
        Konvertiert Indizes in Zeit-Frequenz-Paare.

        Args:
            idxs: Die Indizes der Peaks.
            t: Zeitinformationen des Spektrogramms.
            f: Frequenzinformationen des Spektrogramms.

        Returns:
            Eine Liste von Zeit-Frequenz-Paaren.
        """
        return np.array([(f[i[0]], t[i[1]]) for i in idxs])

    def hash_point_pair(self, p1, p2):
        """
        Erzeugt einen Hashwert für ein Paar von Zeit-Frequenz-Punkten.

        Args:
            p1: Erster Zeit-Frequenz-Punkt.
            p2: Zweiter Zeit-Frequenz-Punkt.

        Returns:
            Ein Hashwert für das Paar von Zeit-Frequenz-Punkten.
        """
        return hash((p1[0], p2[0], p2[1]-p2[1]))

    def target_zone(self, anchor, points, width, height, t):
        """
        Definiert die Zielzone für die Hashberechnung.

        Args:
            anchor: Ankerpunkt.
            points: Liste von Zeit-Frequenz-Punkten.
            width: Breite der Zielzone.
            height: Höhe der Zielzone.
            t: Zeitinformationen des Spektrogramms.

        Yields:
            Punkte innerhalb der Zielzone.
        """
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

    def hash_points(self, points, filename):
        """
        Generiert Hashwerte aus den gefundenen Zeit-Frequenz-Punkten.

        Args:
            points: Liste von Zeit-Frequenz-Punkten.
            filename: Der Dateiname der Audiodatei.

        Returns:
            Eine Liste von Hashwerten.
        """
        hashes = []
        song_id = uuid.uuid5(uuid.NAMESPACE_OID, str(filename)).int
        for anchor in points:
            for target in self.target_zone(
                anchor, points, settings.TARGET_T, settings.TARGET_F, settings.TARGET_START
            ):
                hashes.append((
                    # hash
                    self.hash_point_pair(anchor, target),
                    # time offset
                    anchor[1],
                    # filename
                    str(song_id)
                ))
        return hashes

    def fingerprint_file(self, filename):
        """
        Erzeugt Fingerabdrücke aus einer Audiodatei.

        Args:
            filename: Der Dateiname der Audiodatei.

        Returns:
            Eine Liste von Hashwerten.
        """
        f, t, Sxx = self.file_to_spectrogram(filename)
        peaks = self.find_peaks(Sxx)
        peaks = self.idxs_to_tf_pairs(peaks, t, f)
        return self.hash_points(peaks, filename)
