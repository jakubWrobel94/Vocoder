function plot_fft_carr(f, fft_carr, fft_carr_filtered)
x_lim = 22050;

subplot(211);
plot(f, 10*log10(abs(fft_carr)));
grid on;
title('Carrier signal');
xlim([0 x_lim]);

subplot(212);
plot(f, 10*log10(abs(fft_carr_filtered)));
grid on;
xlabel('frequency [Hz]');
title('Carrier signal filtered');
xlim([0 x_lim]);
end

