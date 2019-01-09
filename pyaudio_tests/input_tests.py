import pyaudio
import numpy as np
import Buffer
from scipy import signal
from numpy import mean, sqrt, square, arange
import matplotlib.pyplot as plt
from audiolazy import lazy_lpc

# audio devices list
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

CHUNK = 512
N_FFT = 2 * CHUNK
N_FILT = 128
FILT_LOW = 50
FILT_UP = 20000
PRE_EMP_COEF = 0.97
RATE = 44100


input_stream = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=44100,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=3)


out_stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True,
                frames_per_buffer=CHUNK,
                input_device_index=5)
data = []
carr_buffer = Buffer.Buffer(CHUNK)
mod_buffer = Buffer.Buffer(CHUNK)
out_buffer = Buffer.Buffer(CHUNK)
window = signal.windows.hann(2*CHUNK)

spectr_filters, filt_freqs = Buffer.get_spectrum_filters(FILT_LOW, FILT_UP, N_FILT, N_FFT, RATE)
filt_coefs = np.zeros((N_FILT, N_FFT))

for i in range(0, 2000):
    data = input_stream.read(CHUNK)
    signal_from_device = np.frombuffer(data, dtype='f4').reshape(-1, 2)

    carr_frame = signal_from_device[:, 0]
    mod_frame = signal_from_device[:, 1]

    carr_rms = sqrt(mean(square(carr_frame)))

    carr_buffer.add_new_chunk(carr_frame)
    mod_buffer.add_new_chunk(mod_frame)

    carr_signal = carr_buffer.get_whole_buffer()
    mod_signal = mod_buffer.get_whole_buffer()

    mod_rms = sqrt(mean(square(mod_signal)))  # why?
    mod_signal = np.multiply(mod_signal, window)
    mod_signal = signal.lfilter([-PRE_EMP_COEF, 1], 1, mod_signal)

    fft_mod = np.abs(np.fft.fft(mod_signal))
    fft_carr = np.fft.fft(carr_signal, N_FFT)

    for filt_idx in range(0, len(filt_coefs)):
        filtered = np.multiply(fft_mod, spectr_filters[(filt_idx, slice(None))])
        filt_coef = np.sum(filtered)
        filt_coefs[(filt_idx, slice(None))] = spectr_filters[(filt_idx, slice(None))] * filt_coef


    curr_coefs = np.sum(filt_coefs, axis=0)
    half = curr_coefs[0:int(N_FFT / 2 + 1)]
    mirrored_half = np.flip(half[1:int(len(half) - 1)])
    fft_coefs = np.concatenate((half, mirrored_half))

    output_signal = np.real(np.fft.ifft(fft_carr * fft_coefs))
    out_rms = sqrt(mean(square(output_signal)))
    gain_factor = carr_rms / out_rms  # ????
    output_signal_windowed = np.float32(np.multiply(output_signal, window) * gain_factor)
    out_buffer.add_to_whole_buffer(output_signal_windowed)

    out = out_buffer.get_old_chunk()
    out_f32 = out.astype(np.float32)
    out_stream.write(out_f32.tobytes())

    carr_buffer.move_chunks()
    mod_buffer.move_chunks()
    out_buffer.move_chunks()


input_stream.stop_stream()
input_stream.close()
out_stream.stop_stream()
out_stream.close()
p.terminate()

