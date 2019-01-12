from Vocoder import LiveStream, FileStream, OutputStream, SettingsLPC, SettingsFFT, VocoderLPC, VocoderFFT

carrier_path = 'wavs/carrier_2.wav'
modulator_path = 'wavs/modulator_2.wav'

#common
CHUNK = 512
PRE_EMP_COEFF = 0.97

#FFT
N_FILT = 80
FILT_LOW = 100
FILT_UP = 20000

#LPC
N_TAPS = 80

settingsFFT = SettingsFFT(CHUNK = CHUNK,
                    N_FILT = N_FILT,
                    FILT_LOW = FILT_LOW,
                    FILT_UP = FILT_UP,
                    PRE_EMP_COEFF = PRE_EMP_COEFF)

settingsLPC = SettingsLPC(CHUNK = CHUNK,
                    N_TAPS = N_TAPS,
                    PRE_EMP_COEFF = PRE_EMP_COEFF)

input_stream = FileStream(carrier_path, modulator_path, CHUNK)
output_stream = OutputStream(channels=input_stream.CHANNELS,
                             rate=input_stream.SAMPLE_RATE,
                             frames_per_buffer=CHUNK,
                             input_device_index=5)

# 2 type of vocoders
vocoder_type = 0
if vocoder_type == 0:
    vocoder = VocoderLPC(settings=settingsLPC,
                      input_stream=input_stream,
                      output_stream=output_stream)
else:
    vocoder = VocoderLPC(settings=settingsLPC,
                  input_stream=input_stream,
                  output_stream=output_stream)
vocoder.initialize()

for _ in range(200):
    vocoder.process()
