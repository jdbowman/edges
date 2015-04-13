function Ri_match = standard_match(f, par)


% Example of format for input parameters
% --------------------------------------
%
% Frequency vector in Hertz: f = [1e6:1e6:1e9]';
%
%
% Coefficients of transmission line: 
% par(1) = offset_Zo    = 50;
% par(2) = offset_delay = 0.0;         % in seconds
% par(3) = offset_loss  = 2.3e9;       % in ohms/second
%
%
% Coefficients of termination resistance: 
% par(4) = Resistance = 50.04
%
%
% Models obtained from Agilent Application Note 1287-11 


%%%% frequency from column to row vector %%%%
f = f';



%%%% termination %%%%
Resistance = par(4);
Zt_match = complex(Resistance*ones(1,length(f)), zeros(1,length(f)));
Rt_match = impedance2gamma(Zt_match,50);




%%%% transmission line %%%%
offset_Zo    = par(1);
offset_delay = par(2);
offset_loss  = par(3);

Zc_match = (offset_Zo + (offset_loss./(2*2*pi*f)).*sqrt(f/1e9)) - 1i*(offset_loss./(2*2*pi*f)).*sqrt(f/1e9);
temp     = ((offset_loss*offset_delay)/(2*offset_Zo))*sqrt(f/1e9);
gl_match = temp + 1i*( (2*pi*f)*offset_delay + temp );




%%%% combined reflection coefficient %%%%
R1       = (Zc_match - 50)./(Zc_match + 50);
ex       = exp(-2*gl_match);
Rt       = Rt_match;
Ri_match = ( R1.*(1 - ex - R1.*Rt) + ex.*Rt ) ./ ( 1 - R1.*(ex.*R1 + Rt.*(1 - ex)) );


%%%% output as column vector %%%%
Ri_match = transpose(Ri_match); % it is complex, so ' is different from transpose()



