function [fir_bank_out] = update_fir_bank(fir_bank, filt_coef)
filt_coef_matrix = repmat(filt_coef', 1, size(fir_bank,2)); 
fir_bank_out = fir_bank .* filt_coef_matrix;
end