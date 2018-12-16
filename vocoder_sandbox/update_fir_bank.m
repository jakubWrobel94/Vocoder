function [fir_bank_out] = update_fir_bank(fir_bank, filt_coef)
fir_bank_out = fir_bank;
for n = 1:size(fir_bank,1)
    fir_bank_out(n, :) = filt_coef(n)* fir_bank(n, :);
end
end