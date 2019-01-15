from Vocoder import VocoderLPC, VocoderFFT, SettingsLPC, SettingsFFT, FileStream, LiveStream, OutputStream
from collections import namedtuple, defaultdict

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
    """
    The class that holds Vocoder object and connects it to the View 
    - defined by VocoderGUI class. 
    """
    def __init__(self):
        """
        When creating the Controller object it uses as default the LPC 
        algorithm.
        """
        self.setLPC()
        p = pyaudio.PyAudio()
        self.devices = [p.get_device_info_by_index(idx)
                        for idx in range(p.get_device_count())]

    def runVocoder(self):
    """Function to run vocoder - simply to execute the process function"""
        self._vocoder.process()

    def set_vocoder_mode(self, mode, **kwargs):
        """
        Method to set the mode of the vocoder
        The kwargs must be provided by keywords arguments:
        * for the Live mode:
            -> 'input_device_index': index of the interface device
            -> 'carr_idx': index of the guitar in this interface
            -> 'mod_idx': index of the vocals (microphone) in the interface
        * for the File mode:
            -> 'carr_path': path to the wave file of the guitar
            -> 'mod_path': path to the wave filel of the modulator - vocal
        """
        if mode is MODE.live:
            assert (
                'input_device_index' in kwargs
                and 'carr_idx' in kwargs
                and 'mod_idx' in kwargs)
            self._vocoder_mode = mode
            self._input_stream = LiveStream(
                    frames_per_buffer=CHUNK,
                    input_device_index=kwargs['input_device_index'],
                    chunk=CHUNK,
                    carr_idx=kwargs['carr_idx'],
                    mod_idx=kwargs['mod_idx'])


        elif mode is MODE.file:
            assert (
                'carr_path' in kwargs
                and 'mod_path' in kwargs)
            self._vocoder_mode = mode
            self._input_stream = FileStream(
                    mod_file_path=kwargs['mod_path'],
                    carr_file_path=kwargs['carr_path'],
                    chunk=CHUNK)

        self._output_stream = OutputStream(
                channels=self._input_stream.CHANNELS,
                rate=self._input_stream.SAMPLE_RATE,
                frames_per_buffer=CHUNK)

        self._vocoder.input_stream = self._input_stream
        self._vocoder.output_stream = self._output_stream
        self._vocoder.initialize()

    def stopVocoder(self):
        pass

    def setFFT(self):
        if not hasattr(self, '_settingsFFT'):
            self._settingsFFT = SettingsFFT(CHUNK = CHUNK,
                                            PRE_EMP_COEFF = PRE_EMP_COEFF,
                                            N_FILT=N_FILT,
                                            FILT_LOW=FILT_LOW,
                                            FILT_UP=FILT_UP)

        self._vocoder = VocoderFFT(settings=self._settingsFFT)

    def setLPC(self):
        if not hasattr(self, '_settingsLPC'):
            self._settingsLPC = SettingsLPC(CHUNK = CHUNK,
                                            N_TAPS = N_TAPS,
                                            PRE_EMP_COEFF = PRE_EMP_COEFF)

        self._vocoder = VocoderLPC(settings=self._settingsLPC)

    def get_input_devices(self):
        """
        Method to return dictionary as follows:
        {"index_of_the_device": {
                                 "name": "name_of_the_device"   
                                 "max": "max_in_channels"
                                }}
        """
        if not hasattr(self, 'input_devices'):
            self.input_devices = defaultdict(dict)
            for device in self.devices:
                in_channels = device.get('maxInputChannels', 0)
                if in_channels:
                    self.input_devices[device['index']] = {
                        'name': device['name'],
                        'max': in_channels
                    }
        return self.input_devices

    def get_output_devices(self):
        """
        Method to return dictionary as follows:
        {"index_of_the_device": {
                                 "name": "name_of_the_device"   
                                 "max": "max_out_channels"
                                }}
        """
        if not hasattr(self, 'output_devices'):
            self.output_devices = defaultdict(dict)
            for device in self.devices:
                in_channels = device.get('maxOutputChannels', 0)
                if in_channels:
                    self.output_devices[device['index']] = {
                        'name': device['name'],
                        'max': in_channels
                    }
        return self.output_devices
