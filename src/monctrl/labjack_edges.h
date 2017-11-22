#pragma once
#include "u3.h"

//-----------------------------------------------
// LabJack Parameters
//-----------------------------------------------
HANDLE 				LABJACK_hDevice;  		// Labjack device handle
u3CalibrationInfo 	LABJACK_caliInfo; 		// calibration info
int 				LABJACK_localID; 		// Labjack ID


//-----------------------------------------------
// LabJack Routines
//-----------------------------------------------
void labjack_open();
void labjack_close();
void labjack_readWeather(double* outRackTemperature, double* outTemperature, double* outHumidity, double* outFrontend);
void labjack_readConduit2(double* outRackTemperature, double *outTemperature, double* outHumidity, double* outFrontend);

//-----------------------------------------------
// CPU temperature routines - must have lm_sensors installed
//-----------------------------------------------
int coretemp_read(double *core1, double* core2, double* core3, double* core4);

