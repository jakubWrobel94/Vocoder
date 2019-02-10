function plot_lpc(lpc)
subplot(211);
plot(lpc);
title('LPC coefficients');
grid on; 

subplot(212);
[lpc_freqz, ~] = freqz(1, lpc);
f = linspace(0, 22050, length(lpc_freqz));
plot(f, 10*log10(lpc_freqz));
title('Frequency response of LPC - IIR filter');
xlabel('frequency [Hz]');
grid on;
end

