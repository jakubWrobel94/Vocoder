function [spectr_filters, filt_freqs] = get_spectrum_filters(f_low, f_up, n_filt, n_fft, fs)
% function to create spectrum filters for checking how much energy is within 
% given frequency band.
% n_filt bands are computed between f_low and f_up frequencies
% fs - sampling frequency
% OUTPUT:
%   spectr_filtres - array of size n_filt X n_fft containing 1 and 0
%   example - n_filt = 2, n_fft = 8, f_low = 0, f_up = nyquist freq :
%   spectr_filtres =  [ 1 1 0 0 0 0 0 0
%                       0 0 1 1 0 0 0 0]
%
%   filt_freqs = frequencies of the filters
filt_freqs = linspace(f_low, f_up, n_filt+1);
f_vector = linspace(0, fs, n_fft);
spectr_filters = zeros(n_filt, n_fft);
for n = 1:length(filt_freqs)-1
    filt_idxs = filt_freqs(n) < f_vector & f_vector < filt_freqs(n+1);
    spectr_filters(n, filt_idxs) = 1;
end
end
