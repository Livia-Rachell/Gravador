import librosa
import numpy as np
from scipy.signal import butter, lfilter
from scipy import stats
from typing import List, Tuple


class AudioLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.audio_data = None
        self.sample_rate = None

    def load_audio(self) -> Tuple[np.ndarray, int]:
        self.audio_data, self.sample_rate = librosa.load(
            self.file_path, sr=None)
        return self.audio_data, self.sample_rate


class AudioFilter:
    def __init__(self, audio_data: np.ndarray, sample_rate: int):
        self.audio_data = audio_data
        self.sample_rate = sample_rate

    def butter_highpass(self, cutoff: float, order: int = 5) -> np.ndarray:
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return lfilter(b, a, self.audio_data)

    def butter_lowpass(self, cutoff: float, order: int = 5) -> np.ndarray:
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return lfilter(b, a, self.audio_data)

    def apply_filters(self, low_cutoff: float, high_cutoff: float) -> np.ndarray:
        high_passed = self.butter_highpass(low_cutoff)
        low_passed = self.butter_lowpass(high_cutoff)
        return low_passed


class NoteDetector:
    def __init__(self, audio_data: np.ndarray, sample_rate: int):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.notes = []

    def detect_notes(self) -> List[Tuple[str, float, float]]:
        onset_env = librosa.onset.onset_strength(
            y=self.audio_data, sr=self.sample_rate)
        times = librosa.times_like(onset_env, sr=self.sample_rate)
        onset_frames = librosa.onset.onset_detect(y=self.audio_data, sr=self.sample_rate, units='samples', hop_length=100, backtrack=False,
                                                  pre_max=20, post_max=20, pre_avg=100, post_avg=100, delta=0.0004, wait=0)
        onset_times = librosa.samples_to_time(onset_frames)
        onset_sample_times = np.concatenate(
            [librosa.time_to_samples(onset_times), [len(self.audio_data)]])

        freqs = []

        fmin = librosa.note_to_hz('C1')
        fmax = librosa.note_to_hz('C8')

        for i in range(len(onset_sample_times) - 1):
            start_sample = onset_sample_times[i]
            end_sample = onset_sample_times[i + 1]

            segment = self.audio_data[start_sample:end_sample]

            f0 = librosa.yin(segment, fmin=fmin, fmax=fmax,
                             sr=self.sample_rate)

            pitch_predominante = stats.mode(f0)[0]

            freqs.append((f'{onset_times[i]:.2f} segundos', librosa.hz_to_note(
                pitch_predominante), pitch_predominante))

        freqs

        for f in freqs:
            print(f"{f[1]} em {f[0]} - [{f[2]:.2f}hz]")

        return self.notes


class NotePrinter:
    def __init__(self, notes: List[Tuple[str, float, float]]):
        self.notes = notes

    def print_notes(self):
        for note, time, frequency in self.notes:
            print(f"{note} em {time:.2f} segundos - [{frequency:.2f}Hz]")


class NoteDetectionPipeline:
    def __init__(self, file_path: str, low_cutoff: float = 80.0, high_cutoff: float = 1000.0):
        self.file_path = file_path
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff

    def run(self):
        audio_loader = AudioLoader(self.file_path)
        audio_data, sample_rate = audio_loader.load_audio()

        # Aplicando os filtros passa-alto e passa-baixo
        audio_filter = AudioFilter(audio_data, sample_rate)
        filtered_audio = audio_filter.apply_filters(
            self.low_cutoff, self.high_cutoff)

        note_detector = NoteDetector(filtered_audio, sample_rate)
        notes = note_detector.detect_notes()

        note_printer = NotePrinter(notes)
        note_printer.print_notes()


# Exemplo de uso
if __name__ == "__main__":
    file_path = "audios/brilha.wav"
    pipeline = NoteDetectionPipeline(file_path)
    pipeline.run()
