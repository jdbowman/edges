function s11_corr = s11_correction_step2(temp, s11)

% This function corrects the s11 measurement (to whom the "step1" correction has been applied)
% to compensate for a temperature of the Match standard different from 27.4
% degrees C, at which the "step1" correction is valid.
%
% s11 is expected to be a complex vector in the frequency range 50-200 MHz,
% ie, 151 points.



%%%% loading parameters %%%%
par_model_1 = load('/media/DATA/s11/auxiliary_data/s11_correction_step2_param1.txt');
par_model_2 = load('/media/DATA/s11/auxiliary_data/s11_correction_step2_param2.txt');


real_s11_corr = zeros(length(s11),1);
imag_s11_corr = zeros(length(s11),1);

%%%% correcting s11 trace %%%%
if (temp >= 20) && (temp <= 27.5)

    for i = 1:length(s11)
    
        %%%% correction relative to 27.4 degrees C %%%%
        correction_real = polyval(par_model_1(i,1:3), temp) - polyval(par_model_1(i,1:3), 27.4);
        correction_imag = polyval(par_model_1(i,4:6), temp) - polyval(par_model_1(i,4:6), 27.4);
    
        
        %%%% correcting data %%%%
        real_s11_corr(i) = real(s11(i)) - correction_real;
        imag_s11_corr(i) = imag(s11(i)) - correction_imag;
        
    end
    
    
    
elseif (temp > 27.5)
    
    for i = 1:length(s11)
    
        %%%% correction relative to 27.4 degrees C %%%%
        correction_real = polyval(par_model_2(i,1:2), temp) - polyval(par_model_1(i,1:3), 27.4);
        correction_imag = polyval(par_model_2(i,3:4), temp) - polyval(par_model_1(i,4:6), 27.4);
    
        
        %%%% correcting data %%%%
        real_s11_corr(i) = real(s11(i)) - correction_real;
        imag_s11_corr(i) = imag(s11(i)) - correction_imag;
    
    end
    
end

s11_corr = complex(real_s11_corr, imag_s11_corr);


