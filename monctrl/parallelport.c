/*
********************************************************************
parallelport.c

HOW TO MAKE SURE YOU HAVE THE RIGHT BASE ADDRESS FOR THE PARALLEL PORT
2013 Nov 5 - JDB (originally from Hamdi)

Actual EDGES code is at the bottom of this file.
********************************************************************

We are using the following PCI parallel port card:
MOSCHIP MCS 9900

Its drivers are at the link below, but we don't need them.  
The instructions in this file are from the PDF that comes with 
the drivers.
http://www.drivers-download.com/en/download.php?id=142&did=113


Step 0: Install the PCI card and boot the computer.

Step 1: Make sure the PCI card was seen when booting up.  Type:

>> dmesg  | grep -i parallel

and you should find a line like this if the card was detected:

[   17.565129] ppdev: user-space parallel port driver

Step 2: Now we need to find the base address and IRQ of the port.
Type the following command:

>> lspci -v

Look for the block describing the parallel port card.  It should 
look like this:

05:00.0 Parallel controller: NetMos Technology Device 9900 (prog-if 03 [IEEE1284])
	Subsystem: Device a000:2000
	Flags: bus master, fast devsel, latency 0, IRQ 14
	I/O ports at dc00 [size=8]
	I/O ports at d880 [size=8]
	Memory at fbbff000 (32-bit, non-prefetchable) [size=4K]
	Memory at fbbfe000 (32-bit, non-prefetchable) [size=4K]
	Capabilities: [50] MSI: Enable- Count=1/1 Maskable- 64bit+
	Capabilities: [78] Power Management version 3
	Capabilities: [80] Express Legacy Endpoint, MSI 00
	Capabilities: [100] Virtual Channel
	Capabilities: [800] Advanced Error Reporting

We are interested in the first I/O port (at dc00 in this instance) which tells us the base address of the parallel port on the card and its IRQ (14 in this instance).

Step 3:  Now, using the I/O port and the IRQ, type:

>> sudo modprobe parport_pc io=0xdc00 irq=14

Step 4: In the edges digitizer code, be sure to set the base address used for the parallel port to the value you found above (0xdc00 in this instance).

That's all.  
********************************************************************
*/

#include <stdio.h>
#include <stdlib.h>
#include <sys/io.h>
#include <time.h>
#include <unistd.h>
#include "parallelport.h"
#define DATA 0x3010 // base address of the  Parallel port PCIe Card
// originally: define DATA 0xdc00 // base address of the SYBA Parallel port PCIe Card 




// -----------------------------------------------
// Send data to the parallel port                 
// -----------------------------------------------
void parport(int pdata)
{
	int i;
	if(pdata == -1) 
	{
		if (ioperm(DATA,3,1)) 
		{
			printf("Sorry, you were not able to gain access to the ports\n");
			printf("You must be root to run this program\n");
			exit(1);
		}
	} else {
		i = 0;  // ant
		if(pdata == 1) i = 2;  // load
		if(pdata == 2) i = 3;  // load + cal
		outb(i,DATA); /* Sends  to the Data Port */
		usleep(100000); // sleep for 0.1 sec
	}
}
