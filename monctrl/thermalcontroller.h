#pragma once
#include <sys/io.h>

// -------------------------------------------------------
// List of modes
// -------------------------------------------------------
// 01  read input1         0x01 - should see about 2500
// 02  read switch voltage 0x02 - should see about 12012
// 03  read input2         0x03 - should see about -26887
// 04  read power          0x04 - should see default 0
// 05  read alarm status   0x05 - should see default 10
// 40  read set point      0x40 - should see default 2500
// 41  read bandwidth      0x41 - should see default 100
// 42  read gain           0x42 - should see default 0
// 43  read derivative     0x43 - should see default 0
// 44  read input1 offset  0x44 - should see default 0
// 45  read input2 offset  0x45 - should see default 0
// 46  read voltage        0x46 - should see default 1200
// 47  read alarm settings 0x47 - should see default 10000
// 48  read cool/heat      0x48 - should see default 2
// 49  read alarm enable   0x49 - should see default 0
// 4a read maxtemp set    0x4a - should see default 1000
// 4b read mintemp set    0x4b - should see default -2000
// 4c read heat side mult 0x4c - should see default 1000
// 4d read output enabled 0x4d - should see default 1
// 4e read cool side mult 0x4e - should see default 1000
// 10 write set point tmp 0x10



// -----------------------------------------------------------------
// thermalcontroller_open
// The thermal controller to is connected via usb-to-serial adapter.
// -----------------------------------------------------------------
int thermalcontroller_open(int usbID)
{
	int usbDevice = 0;
	char buffer[256];
	sprintf(buffer, "stty -F /dev/ttyUSB%d 19200 cs8 -cstopb -parity -icanon min 1 time 1 clocal", usbID);
	system(buffer);
	sprintf(buffer, "/dev/ttyUSB%d", usbID);
	usbDevice = open(buffer, O_RDWR);
	
	return usbDevice;
}


// -----------------------------------------------------------------
// thermalcontroller_close
// -----------------------------------------------------------------
void thermalcontroller_close(int usbDevice)
{
	close(usbDevice); 
}


// -----------------------------------------------------------------
// thermalcontroller_set
// Set the thermal controller temperature point [Degrees Celsius] 
// -----------------------------------------------------------------
int thermalcontroller_set(int usbDevice, double inTemperature)  
{
	int value;
	int mode, check, checkrec, status, i, j, m;
	char command[256], response[256];

	value = 0;
	check = 0;
	mode = 0;
	status = 0;
	value = inTemperature*100;
	i = 0;
	j = 1;
	m = 0;
		
	// Prepare command
	sprintf(command,"*00%02x%08x", mode, value);

	// Add checksum to command
	for(i=0; i<12; i++)
	{
		check += command[i+1];
	}
	sprintf(&command[13],"%02x",(check%256));
	command[15] = 0x0d;
	
	// printf("(stx=%x)",command[0]);
  	// for (i=1;i<15;i++) printf("%1c",command[i]);
	// printf("(etx=%x)\n",command[15]);
  
	// Send the command to the device
	status = 0;
	status = write(usbDevice, command, 16);
	// printf("status %x\n", status);
	
	// Prepare to receive response from device
	for(i=0; i<12 ;i++)
	{
		response[i]=0;
	}
	sleep(1);
	status = 0;
	status = read(usbDevice, response, 12);
	// printf("status: %x, response: %s\n", status, response);
	
	value = 0;
	for(i=0; i<8; i++) 
	{ 
        if (response[8-i] <= '9') 
		{
			m = '0';
		}
		else 
		{
			m = 'a' - 10; 
		}
        
		value += (response[8-i]-m)*j; 
		j = j*16;
	}
	
	printf("received from %02x = %d %f\n", mode, value, value/100.0);
	
	checkrec = 0; 
	for(i=0; i<8 ;i++) 
	{
		checkrec += response[i+1];
	}
	// printf("checkrec %02x\n",(checkrec%256));
			
	return 0;
}



// -----------------------------------------------------------------
// thermalcontroller_read
// -----------------------------------------------------------------
int thermalcontroller_read(int usbDevice, int mode, double *outValue)
{
	int check, checkrec, status, i, j, m, value;
	char command[256], response[256];
	
	// Prepare the command
	value = 2500; 
	sprintf(command,"*00%02x%08x", mode, value);

	check = 0; 
	for(i=0;i<12;i++) 
	{
		check += command[i+1];
	}
	sprintf(&command[13], "%02x", (check%256));
	command[15] = 0x0d;
  
	//for (i=1;i<15;i++) 
	//{
		//printf("%1c",command[i]);
	//}
	//  printf("(etx=%x)\n",command[15]);
  
	// Send the command
	status = 0;
	status = write(usbDevice, command, 16);
	//  printf("status %x\n",status);

	// Get the response
	status = 0;
	sleep(1);
	status = read(usbDevice, response, 12);
	//  printf("status %x resp %s\n",status,resp);
  
	value=0; 
	j=1; 
	for(i=0; i<8; i++) 
	{ 
		if (response[8-i] <= '9')
		{
			m = '0'; 
		}
		else 
		{
			m = 'a' - 10; 
		}
			
		value += (response[8-i]-m)*j; 
		j = j*16;
	}
	// printf("received from %02x = %d %f\n", mode, value);
		
	// Copy the returned value to the output holder
	*outValue = value;
	
	// Double check that everything was good in the response
	checkrec = 0; 
	for(i=0;i<8;i++) 
	{
		checkrec += response[i+1];
	}
	
	value = 0; 
	j = 1; 
	for(i=0; i<2; i++)
	{
		if(response[10-i] <= '9') 
		{
			m = '0';
		}
		else 
		{
			m = 'a' - 10;
		}
		value += (response[10-i]-m)*j; j = j*16;
	}
	
	if(value == (checkrec%256)) 
	{
		// Looks like everything worked OK
		return 1;
	}
	else 
	{
		// Uh oh, we probably are trying to talk to the wrong USB device
		printf("Thermal controller read error (wrong device ID?): %x %x\n", value, checkrec%256);
		return 0;
	}
}

  
// -----------------------------------------------------------------
// thermalcontroller_readall
// -----------------------------------------------------------------
int thermalcontroller_readall(int usbDevice, double *setTemperature, double *actualTemperature, double *actualPower)
{
	double value = 0;
	int iSuccess = 0;
	int iTotalSuccess = 0;
	
	// Read set point temperature
	iSuccess = thermalcontroller_read(usbDevice, 0x40, &value);
	iTotalSuccess += iSuccess;
	*setTemperature = value/100.0;
	
	// Read actual temperature
	iSuccess = thermalcontroller_read(usbDevice, 0x01, &value);
	iTotalSuccess += iSuccess;
	*actualTemperature = value/100.0;
	
	// Read actual power usage
	iSuccess = thermalcontroller_read(usbDevice, 0x04, &value);	
	iTotalSuccess += iSuccess;
	*actualPower = value*100.0/683.0;
	
	if (iTotalSuccess == 3)
	{
		return 1;
	}
	else
	{
		*setTemperature = 0;
		*actualTemperature = 0;
		*actualPower = 0;
		return 0;
	}
}

// -------------------------------------------------------
// thermalcontroller_findusb
// -------------------------------------------------------
int thermalcontroller_findusb()
{
	int usbID = -1;
	int usbDevice = 0;
	int bFound = 0;
	int i = 0;
	double dummy = 0;
	
	while (i >= 0 && i < 2 && bFound == 0)
	{
		usbDevice = thermalcontroller_open(i);
		bFound = thermalcontroller_read(usbDevice, 0x40, &dummy);
		thermalcontroller_close(usbDevice);
		
		if (bFound)
		{	
			usbID = i;
		}
	}
	
	return usbID;
}



	