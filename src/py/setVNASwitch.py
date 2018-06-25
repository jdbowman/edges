#!/usr/bin/env python

import sys
import time
import u3

state = int(sys.argv[1])


#### Labjack ####

# Opening device
d = u3.U3()

# Channels 4-7 digital. 0-3 analog.
d.configU3(FIOAnalog = 15)      
d.configIO(FIOAnalog = 15)

if (state==0):

	# Inverse logic, all outputs OFF
	d.setDOState(4, 1)      
	d.setDOState(5, 1)
	d.setDOState(6, 1)
	d.setDOState(7, 1)
	print('VNA switch set to: OFF\n');

elif (state==1):

	# Activating OPEN with Labjack 
	d.setDOState(4, 0)
	d.setDOState(5, 1)
	d.setDOState(6, 1)
	d.setDOState(7, 0)
	time.sleep(2)
	print('VNA switch set to: OPEN\n');

elif (state==2):

	# Activating SHORT with Labjack 
	d.setDOState(4, 1)
	d.setDOState(5, 0)
	d.setDOState(6, 1)                                                                         
	d.setDOState(7, 0)
	time.sleep(2)
	print('VNA switch set to: SHORT\n');

elif (state==3):

	# Activating MATCH with Labjack 
	d.setDOState(4, 1)
	d.setDOState(5, 1)
	d.setDOState(6, 0)
	d.setDOState(7, 0)
	time.sleep(2)
	print('VNA switch set to: MATCH\n');

elif (state==4):

	# Activating ANTENNA with Labjack
	d.setDOState(4, state = 1)      
	d.setDOState(5, state = 1)
	d.setDOState(6, state = 1)
	d.setDOState(7, state = 0)
	time.sleep(2)
	print('VNA switch set to: ANTENNA\n');

else:

	print('Argument not recognized, used 0-4\n');
