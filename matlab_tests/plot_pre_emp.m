function plot_pre_emp(f, pre_emp_freqz, fft_unf, fft_filt)
x_lim = 10000;
subplot(211);
plot(f(1:length(f)/2), 10*log10(abs(pre_emp_freqz)));
title('Freq. response of pre emphasis filter');
xlim([0, x_lim]);
grid on;
subplot(212);
plot(f, 10*log10(abs(fft_unf)));
hold on;
plot(f, 10*log10(abs(fft_filt)));
title('Modulator signal spectrum');
legend('unfiltered', 'filtered');
xlim([0, x_lim]);
grid on;
hold off;
end

