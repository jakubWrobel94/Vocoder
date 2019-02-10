function [mel_filters, filt_freqs] = get_mel_filters(f_low, f_up, n_filt, n_fft, fs)
m_low = 1125*log(1+f_low/700);
m_up = 1125*log(1+f_up/700);
m_vals = linspace(m_low, m_up, n_filt+2);
filt_freqs = 700*(exp(m_vals/1125) - 1);
f_vector = linspace(0, fs, n_fft);
filter_idx = 1;
mel_filters = zeros(length(filt_freqs)-2, n_fft);

for n = 2:length(filt_freqs)-1
    curr_idxs_pre = filt_freqs(n-1) <=  f_vector & f_vector <= filt_freqs(n);
    curr_idxs_post = filt_freqs(n) <=  f_vector & f_vector <= filt_freqs(n+1);
    mel_filters(filter_idx, curr_idxs_pre) = (f_vector(curr_idxs_pre)-filt_freqs(n-1))/(filt_freqs(n)-filt_freqs(n-1));
    mel_filters(filter_idx, curr_idxs_post) = (filt_freqs(n+1) - f_vector(curr_idxs_post))/(filt_freqs(n+1)-filt_freqs(n));
%     plot(f_vector, mel_filters(filter_idx, :));
%     hold on;
    filter_idx = filter_idx+1;
end
filt_freqs(end) = [];
filt_freqs(1) = [];
end
