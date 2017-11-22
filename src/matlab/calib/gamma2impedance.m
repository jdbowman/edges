function Z=gamma2impedance(s11,Z0)
Z=Z0*(1+s11)./(1-s11);
