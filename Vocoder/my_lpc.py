import pyaudio
import numpy as np
import Buffer
from scipy import signal
from numpy import mean, sqrt, square, arange
import matplotlib.pyplot as plt
from audiolazy import lazy_lpc
import wave
import cProfile, pstats, io
from statsmodels.tsa.stattools import levinson_durbin
def profile(fnc):
    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

@profile
def play():

    p = pyaudio.PyAudio()

    CHUNK = 1024
    PRE_EMP_COEF = 0.8

    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i))

    carrier_path = 'wavs/carrier_2.wav'
    modulator_path = 'wavs/modulator_2.wav'

    mod_wave = wave.open(modulator_path, 'rb')
    carr_wave = wave.open(carrier_path, 'rb')

    FORMAT = p.get_format_from_width(carr_wave.getsampwidth())
    CHANNELS = carr_wave.getnchannels()
    RATE = carr_wave.getframerate()

    out_stream = p.open(format=pyaudio.paFloat32,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=5)
    data = []
    carr_buffer = Buffer.Buffer(CHUNK)
    mod_buffer = Buffer.Buffer(CHUNK)
    out_buffer = Buffer.Buffer(CHUNK)
    window = signal.windows.hann(2*CHUNK)
    int16max = np.iinfo(np.int16).max
    for i in range(0, 100):
        carr_frame = carr_wave.readframes(1024)
        mod_frame = mod_wave.readframes(1024)
        carr_frame = np.frombuffer(carr_frame, np.int16)/int16max
        mod_frame = np.fromstring(mod_frame, np.int16)/int16max
        carr_buffer.add_new_chunk(carr_frame)
        mod_buffer.add_new_chunk(mod_frame)

        carr_signal = carr_buffer.get_whole_buffer()
        mod_signal = mod_buffer.get_whole_buffer()

        carr_rms = sqrt(mean(square(carr_signal)))
        mod_rms = sqrt(mean(square(carr_signal)))
        mod_signal = signal.lfilter([1, -PRE_EMP_COEF], 1, mod_signal)
        #plt.plot(mod_signal)

        X = np.fft.fft(mod_signal)
        R = np.fft.ifft(np.square(np.abs(X)))
        R2 = np.real(R)/len(X)
        ret = levinson_durbin(R2, nlags=20, isacov=False)
        error = ret[0]
        lpc_coef = ret[2]
        plt.plot(lpc_coef)
        output_signal = signal.lfilter([error], lpc_coef,  carr_signal)
        plt.plot(carr_signal)
        plt.plot(output_signal)

        out_rms = sqrt(mean(square(output_signal)))
        gain_factor = mod_rms/out_rms
        output_signal_windowed = np.float32(output_signal * window * gain_factor)


        out_buffer.add_to_whole_buffer(output_signal_windowed)
        out = out_buffer.get_old_chunk()
        out_stream.write(out.astype(np.float32).tobytes())

        carr_buffer.move_chunks()
        mod_buffer.move_chunks()
        out_buffer.move_chunks()

    out_stream.stop_stream()
    out_stream.close()
    p.terminate()

play()