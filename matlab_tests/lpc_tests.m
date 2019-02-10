% load input files, carrier - guitar recording, modulator - voice recording
carrier_path = 'inputs/carrier_2.wav';
modulator_path = 'inputs/modulator_2.wav';

[carrier_wav, carr_fs] = audioread(carrier_path);
[modulator_wav, mod_fs] = audioread(modulator_path);

% truncate both file to same size
wav_len = min([length(carrier_wav), length(modulator_wav)]);
carrier_wav = carrier_wav(1:wav_len);
modulator_wav = modulator_wav(1:wav_len);
% unncoment to change signal to sawtooth or square
%t = (1:wav_len)*1/carr_fs;
% carrier_wav = sawtooth(2*pi*200*t)'*0.5;
% carrier_wav = square(2*pi*200*t)'*0.5;

% CONTROL PARAMETERS
% N_FFT - fft size
% N_FILT - number of bandpass filters 
% FILT_LOW - f of first filter
% FILT_UP - f of last filter
% FILT_ORD - FIR filter order
N_FFT = 1024;
N_FILT = 40;
PRE_EMP_COEF = 0.95;
pre_emp_filter = [ -1*PRE_EMP_COEF, 1];
hi_pass_filter = fir1(100,0.01, 'high');
freqz(hi_pass_filter);
% waves are procesed in chunks with length of fft
chunk_len = N_FFT;
chunk_idx = [1:chunk_len];

output_wav = zeros(1, wav_len);
window = hanning(chunk_len);
chunk_step = chunk_len/2; % frames are overlapping 50%

% filtering mode - if true carrier signal is filtered by FIR filters,
% if false filtering is done by udpating carrier's FFT spectrum and than
% ifft
% both methods sound well (fir kinda better) and their performance is similar, but there is
% some slight difference, check it :)
fir_filtering = true;
f = linspace(0, carr_fs, chunk_len);
tic
% proccesing loop
while chunk_idx(end) <= wav_len
    % get modulator and carrier frames, multiply modulator by window
    % function
    mod_chunk = modulator_wav(chunk_idx);
    plot(f, log10(abs(fft(mod_chunk))));
    hold on;
    mod_chunk = filter(pre_emp_filter, 1, mod_chunk);

    hold off;
    mod_rms = rms(mod_chunk);
    mod_chunk = window.*mod_chunk;
    [lpc_mod, error] = lpc(mod_chunk, N_FILT);
    fft_mod = fft(mod_chunk, N_FFT); % calc fft of modulator
    
    plot_lpc(lpc_mod);
    plot_lpc_spectrums(f, fft_mod, lpc_mod);
    carr_chunk = carrier_wav(chunk_idx);
    carr_rms = rms(carr_chunk);
    
    % update fir filters by filter coefficients
    % do the convolution
    carr_chunk_filtered = filter(1, lpc_mod, carr_chunk');
    
    fft_carr = fft(carr_chunk, N_FFT);
    fft_carr_filtered = fft(carr_chunk_filtered, N_FFT);
    
    plot_fft_carr(f, fft_carr, fft_carr_filtered);
    
    carr_chunk_filtered = carr_chunk_filtered.*window';
    out_rms = rms(carr_chunk_filtered);
    gain_factor = mod_rms/out_rms;
    % concate filtered chunk to output wave
    output_wav(chunk_idx) = output_wav(chunk_idx) + carr_chunk_filtered*gain_factor;
    chunk_idx = chunk_idx + chunk_step;
end

toc
tic
%y = chanvocoder(carrier_wav, modulator_wav, N_FFT, N_FILT, 1/2);
toc
sound(output_wav', carr_fs);
%audiowrite('outputs/output.wav',output_wav,carr_fs);