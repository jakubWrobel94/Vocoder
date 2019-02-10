function plot_lpc_spectrums(f, fft_mod, lpc_mod)
[lpc_freqz, ~] = freqz(1, lpc_mod, 2048);
subplot(211);
plot(f, 10*log10(abs(fft_mod)));
title('Modulator signal spectrum');
grid on;
xlim([0, 22050]);

f = linspace(0, 22050, length(lpc_freqz));
subplot(212);
plot(f, 10*log10(abs(lpc_freqz)));
title('LPC filter frequency response');
grid on;
xlim([0, 22050]);
end

