#include <stdlib.h>
#include <stdio.h>
#include <math.h>

//
// compiling: gcc temperature_humidity.c -o temperature_humidity -lm
// running:   ./temperature_humidity VT VH
// where VT and VH, are the voltages reported by the Labjack in Volts.
// the output is reported in degrees celsius, and percentage.
// 




double temperature(double);
double humidity(double, double);

int main(int argc, char *argv[])
{	
	double VT, VH, TT, HH;
	
	// First argument of the command is the voltage from Thermistor
	VT  = strtof(argv[1], NULL);
	
	
	// Second argument of the command is the voltage from Humidity sensor
	VH  = strtof(argv[2], NULL);
	
	
	// Call functions to obtain temperature and humidity
	TT = temperature(VT);
	HH = humidity(VH, TT);
	
	
	// Returning temperature on screen
	printf("Temperature: %f, Humidity: %f\n", TT, HH);
	return 0;
}





double temperature(double VT)
{
	double R1, R, m1, m2, m3, t_kelvin, t_celsius;
	
	// Conversion of voltage (V as read by labjack) to resistance 
	R1 = 36000;
	R  = (VT * R1) / (5 - VT);


	// Model parameters 
	m1 = -0.000163528;
	m2 =  0.000436689;
	m3 = -6.483802589e-7; 


	// Conversion to temperature using Steinhart–Hart equation
	// 'log' corresponds to Natural Logarithm
	//logR = log(R);
	t_kelvin  = 1 / ( m1 + m2*log(R) + m3*pow(log(R),3) );
	t_celsius = t_kelvin - 273.15;
	return t_celsius;
}




double humidity(double VH, double TT)
{
	double mVH, c1, c2, RH_raw, RH_compensated, c3, c4; 
	
	// Conversion of voltage from sensor to mV (3/2=1.5 is due to voltage divider) 
	mVH = 1000*(1.5)*VH;


	// Model parameters  
	c1 = 0.03892;
	c2 = 42.017;
	

	// Conversion to humidity using equation in datasheet of sensor
	RH_raw = c1* mVH - c2;


	// Correction due to effect of temperature on humidity sensor
	RH_compensated = RH_raw + (TT - 23)*0.05;	// TT in celsius
	return RH_compensated;
}

