function Ri_short = standard_short(f, par)


% Example of format for input parameters
% --------------------------------------
%
% Frequency vector in Hertz: f = [1e6:1e6:1e9]';
%
%
%
% Coefficients of transmission line:  
% par(1) = offset_Zo    = 50;
% par(2) = offset_delay = 31.785e-12;  % in seconds
% par(3) = offset_loss  = 2.36e9;      % in ohms/second
%
%
%
% Coefficients of termination inductance: 
% par(4) = L0 =  2.077e-12;
% par(5) = L1 = -108.5e-24;
% par(6) = L2 =  2.171e-33;
% par(7) = L3 = -0.01e-42;
%
%
% Models obtained from Agilent Application Note 1287-11 


%%%% frequency from column to row vector %%%%
f = f';



%%%% termination %%%%
L0 = par(4);
L1 = par(5);
L2 = par(6);
L3 = par(7);

Lt_short = L0 + L1*f + L2*f.^2 + L3*f.^3;
Zt_short = complex(zeros(1,length(f)), 2*pi*f.*Lt_short);
Rt_short = impedance2gamma(Zt_short,50);




%%%% transmission line %%%%
offset_Zo    = par(1);
offset_delay = par(2);
offset_loss  = par(3);

Zc_short = (offset_Zo + (offset_loss./(2*2*pi*f)).*sqrt(f/1e9)) - 1i*(offset_loss./(2*2*pi*f)).*sqrt(f/1e9);
temp     = ((offset_loss*offset_delay)/(2*offset_Zo))*sqrt(f/1e9);
gl_short = temp + 1i*( (2*pi*f)*offset_delay + temp );




%%%% combined reflection coefficient %%%%
R1       = (Zc_short - 50)./(Zc_short + 50);
ex       = exp(-2*gl_short);
Rt       = Rt_short;
Ri_short = ( R1.*(1 - ex - R1.*Rt) + ex.*Rt ) ./ ( 1 - R1.*(ex.*R1 + Rt.*(1 - ex)) );


%%%% output as column vector %%%%
Ri_short = transpose(Ri_short); % it is complex, so ' is different from transpose()


