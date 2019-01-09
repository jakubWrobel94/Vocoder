import pyaudio
import numpy as np
import Buffer
from scipy import signal
from numpy import mean, sqrt, square, arange
import matplotlib.pyplot as plt
from audiolazy import lazy_lpc
import wave
from Vocoder import LiveStream, FileStream, OutputStream, Settings, Vocoder

# @Buffer.profile
def play():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i))

    carrier_path = 'wavs/carrier_2.wav'
    modulator_path = 'wavs/modulator_2.wav'

    mod_wave = wave.open(modulator_path, 'rb')
    carr_wave = wave.open(carrier_path, 'rb')

    CHUNK = 512
    FORMAT = p.get_format_from_width(carr_wave.getsampwidth())
    CHANNELS = carr_wave.getnchannels()
    RATE = carr_wave.getframerate()

    out_stream = p.open(format=pyaudio.paFloat32,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=5)

    N_FFT = 2 * CHUNK
    N_FILT = 128
    FILT_LOW = 100
    FILT_UP = 10000
    PRE_EMP_COEF = 0.97
    pre_emp_filter = [1, -1 * PRE_EMP_COEF]

    spectr_filters, filt_freqs = Buffer.get_spectrum_filters(FILT_LOW, FILT_UP, N_FILT, N_FFT, RATE)
    filt_coefs = np.zeros((N_FILT, N_FFT))

    # init buffers
    carr_buffer = Buffer.Buffer(CHUNK)
    mod_buffer = Buffer.Buffer(CHUNK)
    out_buffer = Buffer.Buffer(CHUNK)
    window = signal.windows.hann(2 * CHUNK)
    plt.plot(window)
    int16max = np.iinfo(np.int16).max
    filt_window = signal.windows.hann(8)
    for i in range(0, 200):
        # get_freames
        carr_frame = carr_wave.readframes(CHUNK)
        mod_frame = mod_wave.readframes(CHUNK)

        # normalize frames to 0-1
        carr_frame = np.frombuffer(carr_frame, np.int16) / int16max
        mod_frame = np.frombuffer(mod_frame, np.int16) / int16max

        # update buffers
        carr_buffer.add_new_chunk(carr_frame)
        mod_buffer.add_new_chunk(mod_frame)
        carr_signal = carr_buffer.get_whole_buffer()
        mod_signal = mod_buffer.get_whole_buffer()

        mod_rms = sqrt(mean(square(mod_signal)))
        mod_signal = np.multiply(mod_signal, window)
        mod_signal = signal.lfilter([-PRE_EMP_COEF, 1], 1, mod_signal)

        fft_mod = np.abs(np.fft.fft(mod_signal))
        fft_carr = np.fft.fft(carr_signal, N_FFT)

        fft_mod_envelope = signal.lfilter(filt_window, [1], fft_mod)
        plt.plot(fft_mod_envelope)
        # for filt_idx in range(0, len(filt_coefs)):
        #     filtered = np.multiply(fft_mod, spectr_filters[(filt_idx, slice(None))])
        #     filt_coef = np.sum(filtered)
        #     filt_coefs[(filt_idx, slice(None))] = spectr_filters[(filt_idx, slice(None))] * filt_coef

        n_rows = np.shape(spectr_filters)[0]
        filt_coefs = spectr_filters * np.sum(
            spectr_filters * fft_mod, 1).reshape((n_rows, -1))
        
        curr_coefs = np.sum(filt_coefs, axis=0)
        half = curr_coefs[0:int(N_FFT/2+1)]
        mirrored_half = np.flip(half[1:int(len(half)-1)])
        fft_coefs = np.concatenate((half, mirrored_half))
        plt.plot(fft_coefs)
        output_signal = np.real(np.fft.ifft(fft_carr*fft_coefs))
        output_signal = np.real(np.fft.ifft(fft_carr * fft_mod_envelope))
        out_rms = sqrt(mean(square(output_signal)))
        gain_factor = mod_rms / out_rms  # >????????
        output_signal_windowed = np.float32(np.multiply(output_signal, window) * gain_factor)
        out_buffer.add_to_whole_buffer(output_signal_windowed)
        out = out_buffer.get_old_chunk()
        out_f32 = out.astype(np.float32)
        out_stream.write(out_f32.tobytes())

        carr_buffer.move_chunks()
        mod_buffer.move_chunks()
        out_buffer.move_chunks()

    out_stream.stop_stream()
    out_stream.close()
    p.terminate()


# play()
carrier_path = 'wavs/carrier_2.wav'
modulator_path = 'wavs/modulator_2.wav'

CHUNK = 512
# FORMAT = p.get_format_from_width(carr_wave.getsampwidth())

N_FFT = 2 * CHUNK
N_FILT = 128
FILT_LOW = 100
FILT_UP = 10000
PRE_EMP_COEFF = 0.97

settings = Settings(CHUNK = CHUNK,
                    N_FFT = N_FFT,
                    N_FILT = N_FILT,
                    FILT_LOW = FILT_LOW,
                    FILT_UP = FILT_UP,
                    PRE_EMP_COEFF = PRE_EMP_COEFF)

input_stream = FileStream(carrier_path, modulator_path, CHUNK)
output_stream = OutputStream(channels=input_stream.CHANNELS,
                             rate=input_stream.SAMPLE_RATE,
                             frames_per_buffer=CHUNK,
                             input_device_index=5)

vocoder = Vocoder(settings=settings,
                  input_stream=input_stream,
                  output_stream=output_stream)

for _ in range(200):
    vocoder.process()
