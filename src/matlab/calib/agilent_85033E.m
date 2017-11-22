function [o s m] = agilent_85033E(f, resistance_of_match, md)


[op, sp, mp] = fiducial_parameters_85033E(resistance_of_match, md);

o = standard_open(f, op);
s = standard_short(f, sp);
m = standard_match(f, mp);


