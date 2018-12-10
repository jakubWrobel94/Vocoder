function [fir_bank_out] = update_fir_bank(fir_bank, mel_coef)
fir_bank_out = fir_bank;
for n = 1:length(mel_coef)
    fir_bank_out(n, :) = mel_coef(n)* fir_bank(n, :);
end
end