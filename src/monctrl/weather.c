#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sched.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
//#include "stdafx.h"
#include "datetime.h"
#include "labjack_edges.h"

int main(int argc, char **argv)
{ 
	double dRack, dTemp, dHum, dTemp2, dFront;
	int yr, da, hr, mn, sc;
	const char chWeatherFile[1024] = "/home/loco/edges/data/weather2.txt";
	FILE* fid;

	labjack_open();

	labjack_readWeather(&dRack, &dTemp, &dHum, &dTemp2, &dFront);
	printf("Weather - Rack: %5.2f,  Temp: %5.2f,  Hum: %5.2f, Temp2: %5.2f,  Frontend: %5.2f\n", dRack, dTemp, dHum, dTemp2, dFront);

	// Get the time and date
   	toyrday(readclock(), &yr, &da, &hr, &mn, &sc);

	// Attemp to open the log file
  	if ((fid = fopen(chWeatherFile, "a")) == NULL) 
	{
        if ((fid = fopen(chWeatherFile, "w")) == NULL) 
		{
			// Failed to open log file for both append or new
            printf("Weather - Cannot write to: %s\n", chWeatherFile);
            return 0;
        }
	} 

   	// Write to log file
	fprintf(fid, "%4d:%03d:%02d:%02d:%02d  rack_temp %7.2f Kelvin, ambient_temp %7.2f Kelvin, ambient_hum %7.2f percent, frontend %7.2f Kelvin, rcv3_lna %7.2f Kelvin\n", yr, da, hr, mn, sc, dRack, dTemp, dHum, dFront, dTemp2);
 
	fclose(fid);

	labjack_close();

	return 0;
}




