#include "labjack_edges.h"

//-----------------------------------------------
// LabJack 
//-----------------------------------------------

//-----------------------------------------------
// labjack_open
// Open connection to labjack device
//-----------------------------------------------
void labjack_open()
{
    // Open first LABJACK U3 found over USB
	LABJACK_hDevice = NULL;
    LABJACK_localID = -1;
    LABJACK_hDevice = openUSBConnection(LABJACK_localID);

if (LABJACK_hDevice == NULL) {
	printf("Connection failed!\n");
}
printf("%d\n", LABJACK_hDevice);

    // Get calibration information from U3 and store
	// it in the caliInfo parameter so we can use it
	// when reading out values.
    getCalibrationInfo(LABJACK_hDevice, &LABJACK_caliInfo);
}



//-----------------------------------------------
// labjack_close
// Close connection to labjack device
//-----------------------------------------------
void labjack_close()
{
    // ???
}



//-----------------------------------------------
// labjack_readWeather
// Read the temperature and humidity from the 
// EDGES weather station
// -- The humidity sensor is connected to FI02
// -- The temperature sensor is connected to FI03
// -- The frontend temp sensor is connected to FI00
//-----------------------------------------------
void labjack_readWeather(double* outRackTemperature, double* outTemperature, double* outHumidity, double* outFrontend)
{
	double dRack, dTemp, dHum, dFront;
	double dTempVolt, dHumVolt, dFrontVolt;
	double dTempRes, dFrontRes;
	double t1 = -0.000163528;
	double t2 =  0.000436689;
	double t3 = -6.483802589e-7;
	double f1 = 0.001296751267466723;
	double f2 = 0.00019737361897609893;
	double f3 = 3.0403175473012516e-7;
	double h1 = -1.91e-9;
	double h2 =  1.33e-5;
	double h3 =  9.56e-3;
	double h4 = -2.16e1;
	double r1 = 36000.0;
	long DAC1Enable;

	DAC1Enable = 0;
	*outRackTemperature = 0;
	*outTemperature = 0;
	*outHumidity = 0;
	*outFrontend = 0;

	// Read the labjack's built-in temperature sensor
	// channel 32 (special range 3.6V)
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 30, 31, &dRack, 0, 0, 0, 0, 0, 0); 
    *outRackTemperature = dRack;

	// Read the weather station temperature sensor -- FIO3
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 3, 31, &dTempVolt, 0, 0, 0, 0, 0, 0); 

	// Read the frontend temperature sensor -- FI00
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 0, 31, &dFrontVolt, 0, 0, 0, 0, 0, 0); 

	// Read the weather station humidity sensor -- FI02
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 2, 31, &dHumVolt, 0, 0, 0, 0, 0, 0); 

	//printf("TempVolt: %4.5f, HumVolt: %4.5f\n", dTempVolt, dHumVolt);

	// Convert temperature voltage to resistance
	dTempRes = (dTempVolt * r1) / (5.0 - dTempVolt);
	dFrontRes = (dFrontVolt * r1) / (5.0 - dFrontVolt);

	// Convert temperature resistance to temperature (in Kelvin) using 
	// Steinhart-Hart equation 
	dTemp = 1 / (t1 + t2*log(dTempRes) + t3*pow(log(dTempRes), 3.0));
	dFront = 1 / (f1 + f2*log(dFrontRes) + f3*pow(log(dFrontRes), 3.0));
	
	// Adjustment of labjack read voltage
	dHumVolt = dHumVolt * 1000.0 * 1.5;

	// Uncorrected relative humidity (RH in %)
	dHum = h1*pow(dHumVolt, 3) + h2*pow(dHumVolt, 2) + h3*dHumVolt + h4;

	//printf("Weather - Humidity (uncorrected): %4.5f\n", dHum);

	// Corrected relative humidity (using temperature in Kelvin) -- this seems to be small correction
	dHum = dHum + (dTemp - 23.0 - 273.15)*0.05;

	*outTemperature = dTemp; 
	*outFrontend = dFront;
	*outHumidity = dHum;

}


//-----------------------------------------------
// labjack_readWeather
// Read the temperature and humidity from the 
// EDGES weather station
// -- The humidity sensor is connected to FI02
// -- The temperature sensor is connected to FI03
// -- The frontend temp sensor is connected to FI00
//-----------------------------------------------
void labjack_readConduit2(double* outRackTemperature, double* outTemperature, double* outHumidity, double* outFrontend)
{
	double dRack, dTemp, dHum, dFront;
	double dTempVolt, dHumVolt, dFrontVolt;
	double dTempRes, dFrontRes;
	double t1 = -0.000163528;
	double t2 =  0.000436689;
	double t3 = -6.483802589e-7;
	double f1 = 0.001296751267466723;
	double f2 = 0.00019737361897609893;
	double f3 = 3.0403175473012516e-7;
	double h1 = -1.91e-9;
	double h2 =  1.33e-5;
	double h3 =  9.56e-3;
	double h4 = -2.16e1;
	double r1 = 36000.0;
	long DAC1Enable;

	DAC1Enable = 0;
	*outRackTemperature = 0;
	*outTemperature = 0;
	*outHumidity = 0;
	*outFrontend = 0;

	// Read the labjack's built-in temperature sensor
	// channel 32 (special range 3.6V)
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 30, 31, &dRack, 0, 0, 0, 0, 0, 0); 
    *outRackTemperature = dRack;

	// Read the conduit temperature sensor -- FIO3
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 8, 31, &dTempVolt, 0, 0, 0, 0, 0, 0); 

	// Read the frontend temperature sensor -- FI00
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 0, 31, &dFrontVolt, 0, 0, 0, 0, 0, 0); 

	// Read the weather station humidity sensor -- FI02
    eAIN(LABJACK_hDevice, &LABJACK_caliInfo, 1, &DAC1Enable, 14, 31, &dHumVolt, 0, 0, 0, 0, 0, 0); 

	//printf("TempVolt: %4.5f, HumVolt: %4.5f\n", dTempVolt, dHumVolt);

	// Convert temperature voltage to resistance
	dTempRes = (dTempVolt * r1) / (5.0 - dTempVolt);
	dFrontRes = (dFrontVolt * r1) / (5.0 - dFrontVolt);

	// Convert temperature resistance to temperature (in Kelvin) using 
	// Steinhart-Hart equation 
	dTemp = 1 / (t1 + t2*log(dTempRes) + t3*pow(log(dTempRes), 3.0));
	dFront = 1 / (f1 + f2*log(dFrontRes) + f3*pow(log(dFrontRes), 3.0));
	
	// Adjustment of labjack read voltage
	dHumVolt = dHumVolt * 1000.0 * 1.5;

	// Uncorrected relative humidity (RH in %)
	dHum = h1*pow(dHumVolt, 3) + h2*pow(dHumVolt, 2) + h3*dHumVolt + h4;

	//printf("Weather - Humidity (uncorrected): %4.5f\n", dHum);

	// Corrected relative humidity (using temperature in Kelvin) -- this seems to be small correction
	dHum = dHum + (dTemp - 23.0 - 273.15)*0.05;

	*outTemperature = dTemp; 
	*outFrontend = dFront;
	*outHumidity = dHum;

}



//-----------------------------------------------
// coretemp_read
//-----------------------------------------------
int coretemp_read(double *core1, double* core2, double* core3, double* core4)
{
	char buffer[1024];
	char* line;
	FILE *file = popen("sensors", "r");

	if (file)
	{
		while (line = fgets(buffer, sizeof(buffer), file))
		{
			printf("%s\n", line);
		}
		pclose(file);
		
		return 1;
	}
	else
	{
		return 0;
	}
}
