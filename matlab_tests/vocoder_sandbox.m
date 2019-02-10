%load input files, carrier - guitar recording, modulator - voice recording
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
N_FFT = 2048;
N_FILT = 40;
FILT_LOW = 60;
FILT_UP = 22000;
FILT_ORD = 200; 
PRE_EMP_COEF = 0.95;
pre_emp_filter = [ -1*PRE_EMP_COEF, 1];
[pre_emp_freqz, ~] = freqz(pre_emp_filter, 1, N_FFT/2);

% get spectrum filters table -> more info inside function
[spectrum_filts, filt_freqs] = get_spectrum_filters(FILT_LOW, FILT_UP, N_FILT, N_FFT, mod_fs);

% create fir filter bank - create N_FILT fir filters with coeficients are
% stored in array
filt_freqs_norm = [filt_freqs/(mod_fs/2)]; % get frequency bands in normalized (nyquist) units
fir_bank = zeros(N_FILT, FILT_ORD + 1);
for n = 1:1:length(filt_freqs)-1
    fir_bank(n, :) = fir1(FILT_ORD,[filt_freqs_norm(n) filt_freqs_norm(n+1)]);
end

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
fir_filtering = false;
f = linspace(0, carr_fs, N_FFT)
tic
if fir_filtering == true
    % proccesing loop
    while chunk_idx(end) <= wav_len
        % get modulator and carrier frames, multiply modulator by window
        % function
        mod_chunk = modulator_wav(chunk_idx);
        mod_chunk = filter(pre_emp_filter, 1, mod_chunk);
        mod_rms = rms(mod_chunk);
        mod_chunk = window.*mod_chunk;
        
        carr_chunk = carrier_wav(chunk_idx);
        fft_mod = abs(fft(mod_chunk, N_FFT)); % calc fft of modulator
        
        % multiply spectrum by spectrum filters - we get vector with
        % information how much energy is within frequency band, 
        % we add 1 because frequencies  below FILT_DOWN and bigger than FILT_UP are zeros,
        % so to not lose information about this band we set their coef to 1
        filt_coef = fft_mod' * spectrum_filts';
        % update fir filters by filter coefficients 
        fir_filters = update_fir_bank(fir_bank, filt_coef);
        % get one output filter from filter_bank
        filter_out = sum(fir_filters);
        % do the convolution 
        carr_chunk_filtered = filter(filter_out, 1,carr_chunk');
        carr_rms = rms(carr_chunk_filtered);
        gain_factor = mod_rms/carr_rms;
        carr_chunk_filtered = carr_chunk_filtered.*window';
        % concate filtered chunk to output wave
        output_wav(chunk_idx) = output_wav(chunk_idx) + carr_chunk_filtered*gain_factor;
        chunk_idx = chunk_idx + chunk_step;
    end
else
    while chunk_idx(end) <= wav_len
        % get modulator and window frames
        mod_chunk = modulator_wav(chunk_idx);
        mod_rms = rms(mod_chunk);
        fft_pre_emp_befor = fft(mod_chunk);
        
        mod_chunk = filter(pre_emp_filter, 1, mod_chunk);
        fft_pre_emp_after = fft(mod_chunk);
        mod_chunk = window.*mod_chunk;
        
        plot_pre_emp(f, pre_emp_freqz, fft_pre_emp_befor, fft_pre_emp_after);
        
        carr_chunk = carrier_wav(chunk_idx);
        % calc modulator and carrier FFT
        fft_mod = abs(fft(mod_chunk, N_FFT));
        fft_carr = fft(carr_chunk, N_FFT);
        % calculate spectrum filter cooeficients
        filt_coef = (fft_mod' * spectrum_filts');
        % update spectrum filters by filters coefficients = we get envelope
        % of modulator spectrum
        curr_filters = filt_coef*spectrum_filts;
        
        plot_filter_bank(f, spectrum_filts, fft_mod, curr_filters);
        
        % we got envelope of only first half of modulator spectrum so we
        % must mirror it
        mirr_half = curr_filters(end/2:-1:2);
        curr_filters = [curr_filters(1:end/2+1), mirr_half];
        % modify carrier spectrum by envelope of modulator spectrum
        fft_carr_filt = fft_carr.*curr_filters';
        
        plot_carr_filtered(f, fft_carr, curr_filters, fft_carr_filt)
        
        
        % do ifft to go back to time domain
        carr_chunk_filtered =(ifft(fft_carr_filt, N_FFT))'; 
       
        
        plot_time_chunk(carr_chunk_filtered, carr_chunk_filtered.*window');
        
        
        carr_filtered_rms = rms(carr_chunk_filtered);
        carr_chunk_filtered = carr_chunk_filtered.*window'; 
        
        
        gain_factor = mod_rms/carr_filtered_rms;
        if isempty(output_wav)
            output_wav = carr_chunk_filtered;
        else
            output_wav = [output_wav zeros(1, chunk_step)];
            output_wav(end-chunk_len+1:end) = output_wav(end-chunk_len+1:end) + carr_chunk_filtered*gain_factor;
        end
        
        chunk_idx = chunk_idx + chunk_step;
    end
end
toc
tic
% y = chanvocoder(carrier_wav, modulator_wav, N_FFT, N_FILT, 1/2);
toc
sound(output_wav', carr_fs);
%audiowrite('outputs/output.wav',output_wav,carr_fs);

