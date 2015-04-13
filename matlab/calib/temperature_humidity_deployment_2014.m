

function [Tbox RHwea Twea] = temperature_humidity_deployment_2014(file)
% This file is useful for EDGES Deployment 2014
% Temperature sensor: ON-930-44006 
% Humidity sensor:    HM1500LF   

path_coeff = '/media/DATA/s11/auxiliary_data/';


%%%% Reading data %%%%
v = importdata(file);
VTbox = v(:,3);
VHwea = v(:,4);
VTwea = v(:,5);



%%%% Converting voltage to resistance %%%%
R0 = 36000;
Rbox = (VTbox * R0) ./ (5 - VTbox);
Rwea = (VTwea * R0) ./ (5 - VTwea);


%%%% Converting resistance to temperature, using calibration coefficients %%%%

% temperature of box, using thermistor 1
m1 = load([path_coeff 'mount1.dat']);
Tbox = temperature_thermistor(m1(1,1), m1(2,1), m1(3,1), Rbox) - 273.15;

% temperature of weather station, using thermistor 2
m2 = load([path_coeff 'mount2.dat']);
Twea = temperature_thermistor(m2(1,1), m2(2,1), m2(3,1), Rwea) - 273.15;







%%%% Converting voltage to humidity %%%%
mV = VHwea * 1000.0 * 1.5;


% Uncorrected relative humidity (RH in %)
c1 = -1.91e-9;
c2 =  1.33e-5;
c3 =  9.56e-3;
c4 = -2.16e1;
RHwea_unc = c1*(mV.^3) + c2*(mV.^2) + c3*(mV.^1) + c4;


% Corrected relative humidity
RHwea = RHwea_unc + (Twea - 23.0)*0.05;
