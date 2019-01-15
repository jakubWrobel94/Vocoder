import pyaudio
import numpy as np
import Buffer
from scipy import signal
from numpy import mean, sqrt, square, arange
from scipy.linalg import solve_toeplitz
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
    def __init__(self, CHUNK, PRE_EMP_COEFF):
        self.CHUNK = CHUNK
        self.PRE_EMP_COEFF = PRE_EMP_COEFF


class SettingsLPC(Settings):
    def __init__(self, CHUNK, PRE_EMP_COEFF, N_TAPS):
        super(SettingsLPC, self).__init__(CHUNK, PRE_EMP_COEFF)
        self.N_TAPS = N_TAPS


class SettingsFFT(Settings):
    def __init__(self, CHUNK, PRE_EMP_COEFF, N_FILT, FILT_LOW, FILT_UP):
        super(SettingsFFT, self).__init__(CHUNK, PRE_EMP_COEFF)
        self.N_FFT = 2*CHUNK
        self.N_FILT = N_FILT
        self.FILT_LOW = FILT_LOW
        self.FILT_UP = FILT_UP


class Vocoder:
    def __init__(self, settings, input_stream=None, output_stream=None):
        self.settings = settings
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.carr_buffer = Buffer.Buffer(self.settings.CHUNK)
        self.mod_buffer = Buffer.Buffer(self.settings.CHUNK)
        self.output_buffer = Buffer.Buffer(self.settings.CHUNK)

    def get_updated_buffer(self):
        carr_frame, mod_frame, carr_rms = self.input_stream.update_stream()

        self.carr_buffer.add_new_chunk(carr_frame)
        self.mod_buffer.add_new_chunk(mod_frame)

        carr_signal = self.carr_buffer.get_whole_buffer()
        mod_signal = self.mod_buffer.get_whole_buffer()

        return carr_signal, mod_signal, carr_rms


class VocoderLPC(Vocoder):
    def __init__(self, settings, input_stream=None, output_stream=None):
        super(VocoderLPC, self).__init__(settings, input_stream, output_stream)
        self.iir_filter_state = np.array([])

    def initialize(self):
        self.window = signal.windows.hann(2*self.settings.CHUNK)

    def calc_lpc(self, frame):
        n = self.settings.N_TAPS
        fft_frame = np.fft.fft(frame)
        acorr = np.real(np.fft.ifft(fft_frame * np.conj(fft_frame)))
        b = acorr[1:n]
        p = solve_toeplitz((acorr[0:n - 1], acorr[0:n - 1]), b)
        p0 = np.array([1])
        P = np.concatenate((p0, -1 * p))
        return P

    def process(self):
        if not (self.input_stream and self.output_stream):
            raise Exception("You have to provide Input and Output Stream")

        carr_signal, mod_signal, carr_rms = self.get_updated_buffer()

        mod_rms = sqrt(mean(square(mod_signal)))
        mod_signal = np.multiply(mod_signal, self.window)
        mod_signal = signal.lfilter([-self.settings.PRE_EMP_COEFF, 1], 1, mod_signal)

        lpc_coefs = self.calc_lpc(mod_signal)
        if self.iir_filter_state.size == 0:
            self.iir_filter_state = signal.lfilter_zi([1], lpc_coefs)
        output_signal, zf = signal.lfilter([1], lpc_coefs, carr_signal, zi=self.iir_filter_state*carr_signal[0])
        self.iir_filter_state = zf
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


class VocoderFFT(Vocoder):
    def __init__(self, settings, input_stream=None, output_stream=None):
        super(VocoderFFT, self).__init__(settings, input_stream, output_stream)

    def initialize(self):
        self.window = signal.windows.hann(2*self.settings.CHUNK)
        self.spectr_filters, self.filt_freqs = self.get_spectrum_filters()
        self.filt_coefs = np.zeros((self.settings.N_FILT, self.settings.N_FFT))

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

    def process(self):
        if not (self.input_stream and self.output_stream):
            raise Exception("You have to provide Input and Output Stream")

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