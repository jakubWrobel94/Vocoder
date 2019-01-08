import numpy as np
from scipy import signal
import cProfile, pstats, io

class Buffer:

    _old_chunk = []
    _new_chunk = []
    _empty_chunk = []
    _chunk_size = 0

    def __init__(self, chunk_size):
        self._new_chunk = np.zeros((chunk_size, ))
        self._old_chunk = np.zeros((chunk_size, ))
        self._empty_chunk = np.zeros((chunk_size, ))
        self._chunk_size = chunk_size

    def move_chunks(self):
        self._old_chunk = self._new_chunk
        self._new_chunk = self._empty_chunk

    def add_new_chunk(self, chunk_to_add):
        self._new_chunk = chunk_to_add

    def get_whole_buffer(self):
        return np.concatenate((self._old_chunk, self._new_chunk), axis=0)

    def add_to_whole_buffer(self, array_to_add):
        self._old_chunk = self._old_chunk + array_to_add[0:int(self._chunk_size)]
        self._new_chunk = self._new_chunk + array_to_add[int(self._chunk_size):]

    def get_old_chunk(self):
        return self._old_chunk

def get_spectrum_filters(f_low, f_up, n_filt, n_fft, fs):
    filt_freqs = np.linspace(f_low, f_up, n_filt + 1)
    f_vector = np.linspace(0, fs, n_fft)
    spectr_filters = np.zeros((n_filt, n_fft))
    for n in range(0, len(filt_freqs) - 1):
        filt_idxs = (filt_freqs[n] < f_vector) & (f_vector < filt_freqs[n + 1])
        spectr_filters[(n, filt_idxs)] = 1
    return spectr_filters, filt_freqs

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