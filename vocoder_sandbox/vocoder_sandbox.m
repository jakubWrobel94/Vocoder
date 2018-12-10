carrier_path = 'carrier.wav';
modulator_path = 'modulator.wav';

[carrier_wav, carr_fs] = audioread(carrier_path);
[modulator_wav, mod_fs] = audioread(modulator_path);

wav_len = length(modulator_wav);
carrier_wav = carrier_wav(1:wav_len);
N_FFT = 1024;
WIN_LEN = 0.025;
WIN_STEP = 0.01;
N_FILT = 20;
N_CEP = 13;
FILT_LOW = 200;
FILT_UP = 4000;

[mel_filts, filt_freqs] = get_mel_filters(FILT_LOW, FILT_UP, N_FILT, N_FFT, mod_fs);
filt_freqs_norm = [filt_freqs/(mod_fs/2)];
fir_bound = FILT_LOW/(carr_fs/2);
for i = 1:length(filt_freqs_norm)-1
    fir_bound(end+1) = (filt_freqs_norm(i) + filt_freqs_norm(i+1))/2;
end
fir_bound(end+1) = FILT_UP/(carr_fs/2);

fir_bank = [];
for n = 1:length(filt_freqs)
    fir_bank(end+1, :) = fir1(50,[fir_bound(n) fir_bound(n+1)]);
end

mel_filts = mel_filts';
chunk_len = WIN_LEN * carr_fs;
chunk_idx = [1:chunk_len];
mel_coef = [];

output_wav = [];
window = hamming(chunk_len);
fir_filters = fir_bank;
pre_post_zeros = zeros((N_FFT - chunk_len)/2, 1);
while chunk_idx(end) <= wav_len
    mod_chunk = modulator_wav(chunk_idx);
    mod_chunk = window.*mod_chunk;
    fft_mod = (1/N_FFT)*abs(fft(mod_chunk, N_FFT)).^2;
    mel_coef = (log10((fft_mod' * mel_filts)/0.0001))/20;
    fir_filters = update_fir_bank(fir_bank, mel_coef);
    filter_out = sum(fir_filters);
    carr_chunk = carrier_wav(chunk_idx);
    carr_chunk_filtered = filter(filter_out, 1,carr_chunk');
    output_wav = [output_wav, carr_chunk_filtered];
    chunk_idx = chunk_idx + chunk_len;
end
sound(output_wav', carr_fs);
audiowrite('wynik.wav',output_wav,carr_fs);