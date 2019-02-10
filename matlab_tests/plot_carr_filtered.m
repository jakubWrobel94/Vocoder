function plot_carr_filtered(f, fft_carr, spectral_filts, fft_carr_filtered)
x_lim = 22050;
subplot(311);
plot(f, 10*log10(abs(fft_carr)));
title('Carrier signal spectrum');
xlim([0 x_lim]);
grid on;

subplot(312);
plot(f, 10*log10(abs(spectral_filts)));
title('Modulator spectral energy bands');
xlim([0 x_lim]);
grid on;

subplot(313);
plot(f, 10*log10(abs(fft_carr_filtered)));
title('Filtered carrier signal spectrum');
xlim([0 x_lim]);
grid on;
xlabel('frequency [Hz]');
end