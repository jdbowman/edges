function Ri_open = standard_open(f, par)


% Example of format for input parameters
% --------------------------------------
%
% Frequency vector in Hertz: f = [1e6:1e6:1e9]';
%
% Coefficients of transmission line:  
% par(1) = offset_Zo    = 50;
% par(2) = offset_delay = 29.243e-12;  % in seconds
% par(3) = offset_loss  = 2.2e9;       % in ohms/second 
%
%
% Coefficients of termination capacitance: 
% par(4) = C0 =  49.43e-15;
% par(5) = C1 = -310.1e-27;
% par(6) = C2 =  23.17e-36;
% par(7) = C3 = -0.1597e-45;
%
%
%
%
% Models obtained from Agilent Application Note 1287-11 


%%%% frequency from column to row vector %%%%
f = f';



%%%% termination %%%%
C0 = par(4);
C1 = par(5);
C2 = par(6);
C3 = par(7);

Ct_open = C0 + C1*f + C2*f.^2 + C3*f.^3;
Zt_open = complex(zeros(1,length(f)), -1*ones(1,length(f))./(2*pi*f.*Ct_open));
Rt_open = impedance2gamma(Zt_open,50);




%%%% transmission line %%%%
offset_Zo    = par(1);
offset_delay = par(2);
offset_loss  = par(3);

Zc_open  = (offset_Zo + (offset_loss./(2*2*pi*f)).*sqrt(f/1e9)) - 1i*(offset_loss./(2*2*pi*f)).*sqrt(f/1e9);
temp     = ((offset_loss*offset_delay)/(2*offset_Zo))*sqrt(f/1e9);
gl_open  = temp + 1i*( (2*pi*f)*offset_delay + temp );




%%%% combined reflection coefficient %%%%
R1      = (Zc_open - 50)./(Zc_open + 50);
ex      = exp(-2*gl_open);
Rt      = Rt_open;
Ri_open = ( R1.*(1 - ex - R1.*Rt) + ex.*Rt ) ./ ( 1 - R1.*(ex.*R1 + Rt.*(1 - ex)) );


%%%% output as column vector %%%%
Ri_open = transpose(Ri_open); % it is complex, so ' is different from transpose()


