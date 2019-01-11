import pyaudio
import numpy as np
import Buffer
from scipy import signal
from numpy import mean, sqrt, square, arange
import matplotlib.pyplot as plt
from audiolazy import lazy_lpc
import wave


class Stream:
    def __init__(self):
        self.p = pyaudio.PyAudio()


class LiveStream(Stream):
    def __init__(self, channels, rate, frames_per_buffer, 
            input_device_index, chunk, carr_idx, mod_idx):
        super(LiveStream, self).__init__()
        self.carr_idx = carr_idx
        self.mod_idx = mod_idx
        self.CHUNK = chunk
        self.SAMPLE_RATE = 44100
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=channels,
                                  rate=rate,
                                  input=True,
                                  frames_per_buffer=frames_per_buffer,
                                  input_device_index=input_device_index)


    def update_stream(self):
        data = self.stream.read(self.CHUNK)
        signal_from_device = np.frombuffer(data, dtype='f4').reshape(-1, 2)

        carr_frame = signal_from_device[:, self.carr_idx]
        mod_frame = signal_from_device[:, self.mod_idx]
        carr_rms = sqrt(mean(square(carr_frame)))

        return carr_frame, mod_frame, carr_rms


class FileStream(Stream):
    def __init__(self, carr_file_path, mod_file_path, chunk):
        super(FileStream, self).__init__()
        self.carr_wave = wave.open(carr_file_path, 'rb')
        self.mod_wave = wave.open(mod_file_path, 'rb')
        self.CHUNK = chunk
        self.int16max = np.iinfo(np.int16).max
        self.SAMPLE_RATE = self.carr_wave.getframerate()
        self.CHANNELS = self.carr_wave.getnchannels()

    def update_stream(self):
        carr_frame = self.carr_wave.readframes(self.CHUNK)
        mod_frame = self.mod_wave.readframes(self.CHUNK)

        carr_frame = np.frombuffer(carr_frame, np.int16) / self.int16max
        mod_frame = np.frombuffer(mod_frame, np.int16) / self.int16max

        return carr_frame, mod_frame, None


class OutputStream(Stream):
    def __init__(self, channels, rate, frames_per_buffer, 
            input_device_index):
        super(OutputStream, self).__init__()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=channels,
                                  rate=rate,
                                  output=True,
                                  frames_per_buffer=frames_per_buffer,
                                  input_device_index=input_device_index)


class Settings:
    def __init__(self, CHUNK, N_FFT, N_FILT, FILT_LOW, FILT_UP, PRE_EMP_COEFF):
        self.CHUNK = CHUNK
        self.N_FFT = N_FFT
        self.N_FILT = N_FILT
        self.FILT_LOW = FILT_LOW
        self.FILT_UP = FILT_UP
        self.PRE_EMP_COEFF = PRE_EMP_COEFF


class Vocoder:
    def __init__(self, settings, input_stream, output_stream):
        self.settings = settings
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.carr_buffer = Buffer.Buffer(self.settings.CHUNK)
        self.mod_buffer = Buffer.Buffer(self.settings.CHUNK)
        self.output_buffer = Buffer.Buffer(self.settings.CHUNK)
        self.initialize()

    def initialize(self):
        self.window = signal.windows.hann(2*self.settings.CHUNK)
        self.spectr_filters, self.filt_freqs = self.get_spectrum_filters()
        self.filt_coefs = np.zeros((self.settings.N_FILT, self.settings.N_FFT))

    def read_frames():
        pass

    def get_updated_buffer(self):
        carr_frame, mod_frame, carr_rms = self.input_stream.update_stream()

        self.carr_buffer.add_new_chunk(carr_frame)
        self.mod_buffer.add_new_chunk(mod_frame)

        carr_signal = self.carr_buffer.get_whole_buffer()
        mod_signal = self.mod_buffer.get_whole_buffer()

        return carr_signal, mod_signal, carr_rms


    def process(self):
        carr_signal, mod_signal, carr_rms = self.get_updated_buffer()

        mod_rms = sqrt(mean(square(mod_signal)))
        mod_signal = np.multiply(mod_signal, self.window)
        mod_signal = signal.lfilter([-self.settings.PRE_EMP_COEFF, 1], 1, mod_signal)

        fft_mod = np.abs(np.fft.fft(mod_signal))
        fft_carr = np.fft.fft(carr_signal, self.settings.N_FFT)

        n_rows = np.shape(self.spectr_filters)[0]
        filt_coefs = self.spectr_filters * np.sum(
            self.spectr_filters * fft_mod, 1).reshape((n_rows, -1))

        curr_coefs = np.sum(filt_coefs, axis=0)
        half = curr_coefs[0:int(self.settings.N_FFT / 2 + 1)]
        mirrored_half = np.flip(half[1:int(len(half) - 1)])
        fft_coefs = np.concatenate((half, mirrored_half))

        output_signal = np.real(np.fft.ifft(fft_carr * fft_coefs))
        out_rms = sqrt(mean(square(output_signal)))
        gain_factor = carr_rms / out_rms if  carr_rms else mod_rms / out_rms
        output_signal_windowed = np.float32(np.multiply(output_signal, self.window) * gain_factor)
        self.output_buffer.add_to_whole_buffer(output_signal_windowed)

        out = self.output_buffer.get_old_chunk()
        out_f32 = out.astype(np.float32)
        self.output_stream.stream.write(out_f32.tobytes())

        self.carr_buffer.move_chunks()
        self.mod_buffer.move_chunks()
        self.output_buffer.move_chunks()


    def get_spectrum_filters(self):
        filt_freqs = np.linspace(self.settings.FILT_LOW, 
                                 self.settings.FILT_UP,
                                 self.settings.N_FILT + 1)
        f_vector = np.linspace(0, 
            self.input_stream.SAMPLE_RATE, 
            self.settings.N_FFT)
        spectr_filters = np.zeros((self.settings.N_FILT, self.settings.N_FFT))
        for n in range(0, len(filt_freqs) - 1):
            filt_idxs = (filt_freqs[n] < f_vector) & (f_vector < filt_freqs[n + 1])
            spectr_filters[(n, filt_idxs)] = 1
        return spectr_filters, filt_freqs

