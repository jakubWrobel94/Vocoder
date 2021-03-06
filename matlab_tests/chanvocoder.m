function y = chanvocoder(carrier, modul, chan, numband, overlap)
% y = chanvocoder(carrier, modul, chan, numband, overlap)
% The Channel Vocoder modulates the carrier signal with the modulation signal
% chan = number of channels         (e.g., 512)
% numband = number of bands (<chan) (e.g., 32)
% overlap = window overlap          (e.g., 1/4)

if numband>chan, error('# bands must be < # channels'), end
[rc, cc]   = size(carrier); if cc>rc, carrier = carrier'; end
[rm, cm]   = size(modul);   if cm>rm, modul = modul'; end
st         = min(rc,cc);                         % stereo or mono?
if st~= min(rm,cm), error('carrier and modulator must have same number of tracks'); end
len        = min(length(carrier),length(modul)); % find shortest length
carrier    = carrier(1:len,1:st);                % shorten carrier if needed
modul      = modul(1:len,1:st);                  % shorten modulator if needed
L          = 2*chan;                             % window length/FFT length
w          = hanning(L); if st==2, w=[w w]; end  % window/ stereo window
bands      = 1:round(chan/numband):chan;         % indices for frequency bands     
bands(end) = chan;
y          = zeros(len,st);                      % output vector
ii         = 0;
while ii*L*overlap+L <= len
    ind    = round([1+ii*L*overlap:ii*L*overlap+L]);
    FFTmod = fft( modul(ind,:) .* w );    % window & take FFT of modulator
    FFTcar = fft( carrier(ind,:) .* w );  % window & take FFT of carrier  
    syn    = zeros(chan,st);              % place for synthesized output
    for jj = 1:numband-1                  % for each frequency band
        b        = [bands(jj):bands(jj+1)-1]; % current band
        syn(b,:) = FFTcar(b,:)*diag(mean(abs(FFTmod(b,:))));
    end                                   % take product of spectra
    midval   = FFTmod(1+L/2,:).*FFTcar(1+L/2,:); % midpoint is special
    synfull  = [syn; midval; flipud( conj( syn(2:end,:) ) );]; % + and - frequencies
    timsig   = real( ifft(synfull) );     % invert back to time
    y(ind,:) = y(ind,:) + timsig;         % add back into time waveform   
    ii       = ii+1;
end
y = 0.8*y/max(max(abs(y)));               % normalize output