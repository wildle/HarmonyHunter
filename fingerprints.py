import settings
import numpy as np
import uuid
import io
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter

class Fingerprint:

    def file_to_spectrogram(self, uploaded_file):
        audio_content = uploaded_file.read()
        a = AudioSegment.from_wav(io.BytesIO(audio_content)).set_channels(1).set_frame_rate(settings.SAMPLE_RATE)
        audio = np.frombuffer(a.raw_data, np.int16)
        return self.my_spectrogram(audio)

    def my_spectrogram(self, audio):
        nperseg = int(settings.SAMPLE_RATE * settings.FFT_WINDOW_SIZE)
        return spectrogram(audio, settings.SAMPLE_RATE, nperseg=nperseg)

    def find_peaks(self, Sxx):
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
        return np.array([(f[i[0]], t[i[1]]) for i in idxs])

    def hash_point_pair(self, p1, p2):
        return hash((p1[0], p2[0], p2[1]-p2[1]))

    def target_zone(self, anchor, points, width, height, t):
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
        f, t, Sxx = self.file_to_spectrogram(filename)
        peaks = self.find_peaks(Sxx)
        peaks = self.idxs_to_tf_pairs(peaks, t, f)
        return self.hash_points(peaks, filename)
