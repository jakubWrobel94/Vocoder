function plot_time_chunk(chunk, chunk_windowed)
subplot(211)
plot(chunk);
title('Signal before windowing');
legend('filtered signal', 'window function');
xlim([1, length(chunk)]);
grid on;

subplot(212);
plot(chunk_windowed);
title('Signal after windowing');
xlim([1, length(chunk)]);
grid on;
end
