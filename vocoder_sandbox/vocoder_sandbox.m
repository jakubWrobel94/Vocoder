% load input files, carrier - guitar recording, modulator - voice recording
carrier_path = 'inputs/carrier_2.wav';
modulator_path = 'inputs/modulator_2.wav';

[carrier_wav, carr_fs] = audioread(carrier_path);
[modulator_wav, mod_fs] = audioread(modulator_path);

% truncate both file to same size
if length(carrier_wav) > length(modulator_wav)
    wav_len = length(modulator_wav);
    carrier_wav = carrier_wav(1:wav_len);
else
    wav_len = length(carrier_wav);
    carrier_wav = modulator_wav(1:wav_len);
end

% CONTROL PARAMETERS
% N_FFT - fft size
% N_FILT - number of bandpass filters 
% FILT_LOW - f of first filter
% FILT_UP - f of last filter
% FILT_ORD - FIR filter order
N_FFT = 1024;
N_FILT = 101;
FILT_LOW = 100;
FILT_UP = 20000;
FILT_ORD = 100; 
% get spectrum filters table -> more info inside function
[spectrum_filts, filt_freqs] = get_spectrum_filters(FILT_LOW, FILT_UP, N_FILT, N_FFT, mod_fs);
filt_freqs_norm = [filt_freqs/(mod_fs/2)]; % get frequency bands in normalized (nyquist) units

% create fir filter bank - create N_FILT fir filters with coeficients are
% stored in array
fir_bank = zeros(N_FILT, FILT_ORD + 1);
for n = 1:1:length(filt_freqs)-1
    fir_bank(n, :) = fir1(FILT_ORD,[filt_freqs_norm(n) filt_freqs_norm(n+1)]);
end

% waves are procesed in chunks with length of fft
chunk_len = N_FFT;
chunk_idx = [1:chunk_len];
filt_coef = [];

output_wav = [];
window = hanning(chunk_len);
chunk_step = chunk_len/2; % frames are overlapping 50%

% filtering mode - if true carrier signal is filtered by FIR filters,
% if false filtering is done by udpating carrier's FFT spectrum and than
% ifft
% both methods sound well (fir kinda better) and their performance is similar, but there is
% some slight difference, check it :) 
fir_filtering = true;
tic
if fir_filtering == true
    % proccesing loop
    while chunk_idx(end) <= wav_len
        % get modulator and carrier frames, multiply modulator by window
        % function
        mod_chunk = modulator_wav(chunk_idx);
        mod_chunk = window.*mod_chunk;
        carr_chunk = carrier_wav(chunk_idx);
        fft_mod = abs(fft(mod_chunk, N_FFT)); % calc fft of modulator
        
        % multiply spectrum by spectrum filters - we get vector with
        % information how much energy is within frequency band, 
        % we add 1 because frequencies  below FILT_DOWN and bigger than FILT_UP are zeros,
        % so to not lose information about this band we set their coef to 1
        filt_coef = fft_mod' * spectrum_filts'+1;
        % update fir filters by filter coefficients 
        fir_filters = update_fir_bank(fir_bank, filt_coef);
        % get one output filter from filter_bank
        filter_out = sum(fir_filters);
        % do the convolution 
        carr_chunk_filtered = filter(filter_out, 1,carr_chunk');
        % output chunk must be multiplied by window function to get rid
        % of some side artifacts after filtering
        % it's devided by some int to prevent distortion - signal level is raised
        % - TODO handle it in some smarter way
        carr_chunk_filtered = carr_chunk_filtered.*window'/30;
        
        % concate filtered chunk to output wave
        if isempty(output_wav)
            output_wav = carr_chunk_filtered;
        else
            % this weird indexing handles frames overlapping
            output_wav = [output_wav zeros(1, chunk_step)];
            output_wav(end-chunk_len+1:end) = output_wav(end-chunk_len+1:end) + carr_chunk_filtered;
        end
        chunk_idx = chunk_idx + chunk_step;
    end
else
    while chunk_idx(end) <= wav_len
        % get modulator and window frames
        mod_chunk = modulator_wav(chunk_idx);
        mod_chunk = window.*mod_chunk;
        carr_chunk = carrier_wav(chunk_idx);
        % calc modulator and carrier FFT
        fft_mod = abs(fft(mod_chunk, N_FFT));
        fft_carr = abs(fft(carr_chunk, N_FFT));
        % calculate spectrum filter cooeficients
        filt_coef = (fft_mod' * spectrum_filts');
        % update spectrum filters by filters coefficients = we get envelope
        % of modulator spectrum
        curr_filters = filt_coef*spectrum_filts+1;
        % we got envelope of only first half of modulator spectrum so we
        % must mirror it
        mirr_half = curr_filters(end/2:-1:2);
        curr_filters = [curr_filters(1:end/2+1), mirr_half];
        % modify carrier spectrum by envelope of modulator spectrum
        fft_carr_filt = fft_carr.*curr_filters';
        % do ifft to go back to time domain
        carr_chunk_filtered =(ifft(fft_carr_filt, N_FFT)/sqrt(N_FFT))';
        carr_chunk_filtered = carr_chunk_filtered.*window';
        
        if isempty(output_wav)
            output_wav = carr_chunk_filtered;
        else
            output_wav = [output_wav zeros(1, chunk_step)];
            output_wav(end-chunk_len+1:end) = output_wav(end-chunk_len+1:end) + carr_chunk_filtered;
        end
        
        chunk_idx = chunk_idx + chunk_step;
    end
end
toc
sound(output_wav', carr_fs);
% audiowrite('outputs/wynik_5.wav',output_wav,carr_fs);