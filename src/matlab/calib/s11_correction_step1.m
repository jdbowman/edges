function gamma_corrected = s11_correction_step1(gamma_input)




%%%% loading calibration file %%%%
folder = '/media/DATA/s11/auxiliary_data/';
d = load([folder 's11_correction_step1.txt']);
s11_corr    = complex(d(:,2), d(:,3));
s12s21_corr = complex(d(:,4), d(:,5));
s22_corr    = complex(d(:,6), d(:,7));



%%%% applying correction %%%%
gamma_corrected = (gamma_input - s11_corr) ./ (s12s21_corr + s22_corr.*(gamma_input - s11_corr));



