
//  cc -o  labjack_control  labjack_control.c  u3.o  -lm -llabjackusb 

#include "u3.h"
#include <unistd.h>
#include <stdio.h>

int main(int argc,  char *argv[])
{
    HANDLE hDevice;
    u3CalibrationInfo caliInfo;
    int localID;
    long DAC1Enable, error;
    double dblVoltage;

    //Open first found U3 over USB
    localID = -1;
    if( (hDevice = openUSBConnection(localID)) == NULL )
        goto done;

    //Get calibration information from U3
    if( getCalibrationInfo(hDevice, &caliInfo) < 0 )
        goto close;

double x = atof(argv[1]), dac0 ; // convert character to double

if (x == 0 ) dac0=0;
if (x == 1 ) dac0=5;


    //Set DAC0 to x volts.
    if( (error = eDAC(hDevice, &caliInfo, 0, 0, dac0 , 0, 0, 0)) != 0 )
      goto close;
    printf("\nCalling eAIN to read voltage from AIN3\n");
    if( (error = eAIN(hDevice, &caliInfo, 1, &DAC1Enable, 3, 31, &dblVoltage, 0, 0, 0, 0, 0, 0)) != 0 )
        goto close;
    printf("AIN3 value = %.3f\n", dblVoltage);

    //sleep(1);
close:
    if( error > 0 )
   //     printf("Received an error code of %ld\n", error);
    closeUSBConnection(hDevice);
done:
    return 0;
}


