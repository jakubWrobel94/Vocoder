function plot_filter_bank(f, filter_bank, fft_mod, filt_coefs)
x_lim = 22050;
subplot(311);
plot(f, filter_bank');
title('Spectral filters bank');
xlim([0 x_lim]);
ylim([0 1.2]);

subplot(312);
plot(f, 10*log10(abs(fft_mod)));
title('Modulator signal spectrum');
xlim([0 x_lim]);
grid on;

subplot(313);
plot(f, filt_coefs);
title('Spectral energy within given filters');
xlim([0 x_lim]);
grid on;
xlabel('frequency [Hz]');
end