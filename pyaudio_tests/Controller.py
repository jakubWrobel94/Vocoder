from Vocoder import VocoderLPC, VocoderFFT, SettingsLPC, SettingsFFT, FileStream, LiveStream, OutputStream
from collections import namedtuple

import pyaudio
#  variable of type MODE can only be of type 'file' or 'live'
MODE = namedtuple('MODE', 'file live')._make(range(2))

CHUNK = 512
N_FFT = 2 * CHUNK
N_FILT = 128
FILT_LOW = 100
FILT_UP = 10000
PRE_EMP_COEFF = 0.97
N_TAPS = 80

class Controller:
    def __init__(self):
        self._settings = SettingsLPC(CHUNK = CHUNK,
                    N_TAPS = N_TAPS,
                    PRE_EMP_COEFF = PRE_EMP_COEFF)

        self._vocoder = VocoderLPC(settings=self._settings)

    def set_vocoder_mode(self, mode, *args, **kwargs):
        if mode is MODE.live:
            assert (
                'input_device_index' in kwargs
                and 'carr_idx' in kwargs
                and 'mod_idx' in kwargs)
            self._vocoder_mode = mode
            #  do same thing as below


        elif mode is MODE.file:
            assert (
                'carr_path' in kwargs
                and 'mod_path' in kwargs)
            self._vocoder_mode = mode
            self._input_stream = FileStream(
                    carr_file_path=kwargs['carr_path'],
                    mod_file_path=kwargs['mod_path'],
                    chunk=CHUNK)
            self._output_stream = OutputStream(
                    channels=self._input_stream.CHANNELS,
                    rate=self._input_stream.SAMPLE_RATE,
                    frames_per_buffer=CHUNK,
                    input_device_index=5)

        self._vocoder.input_stream = self._input_stream
        self._vocoder.output_stream = self._output_stream
        self._vocoder.initialize()

    def runVocoder(self):
        # print("this works in controller class, and runs the Vocoder")
        self._vocoder.process()

    def stopVocoder(self):
        print ("this works in controller class, and stops the Vocoder")

    @staticmethod
    def get_devices():
        p = pyaudio.PyAudio()
        devices = {idx: p.get_device_info_by_index(idx)['name'] 
            for idx in range(p.get_device_count())}
        print(devices)


