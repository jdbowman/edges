function [op, sp, mp] = fiducial_parameters_85033E(R, md)


% parameters of open
open_off_Zo    = 50; 
open_off_delay = 29.243e-12;
open_off_loss  = 2.2*1e9;
open_C0 =  49.43e-15; 
open_C1 = -310.1e-27;
open_C2 =  23.17e-36;
open_C3 = -0.1597e-45;

op = [open_off_Zo open_off_delay open_off_loss open_C0 open_C1 open_C2 open_C3];



% parameters of short
short_off_Zo    = 50; 
short_off_delay = 31.785e-12;
short_off_loss  = 2.36*1e9;
short_L0 =  2.077e-12;
short_L1 = -108.5e-24;
short_L2 =  2.171e-33;
short_L3 = -0.01e-42;

sp = [short_off_Zo short_off_delay short_off_loss short_L0 short_L1 short_L2 short_L3];



% parameters of match
match_off_Zo    = 50;

if md == 0
    match_off_delay = 0;
elseif md == 1
    match_off_delay = 30e-12;   % rough average between open and short
end

match_off_loss  = 2.3*1e9;
match_R         = R;

mp = [match_off_Zo match_off_delay match_off_loss match_R];

