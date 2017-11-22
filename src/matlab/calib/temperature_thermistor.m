function t=temperature_thermistor(a1, a2, a3, R)

% t in Kelvin
t = 1./(a1 + a2*log(R) + a3*(log(R)).^3);




