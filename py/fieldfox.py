
#!/usr/bin/env python

import socket
import time
import os as o
import ftplib 
import u3


#### Input quantities ####
FILE_VNA       = 'EDGES.s1p'
DATA_FOLDER_PC = '/media/DATA/s11/antenna_s11/20150227/' 
FILE_VOLTAGE   = DATA_FOLDER_PC + 'voltage_' + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + '.txt'

TCP_IP         = '172.20.1.250'
TCP_PORT       = 5025







s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))


MESSAGE = '*IDN?\n'
s.send(MESSAGE)

data = s.recv(100)
print "---------------------------------------------------------------------------"
print " "
print "Connected: ", data
print "---------------------------------------------------------------------------"


MESSAGE = 'SENS:FREQ:START 50e6;*OPC?\n'
s.send(MESSAGE)

MESSAGE = 'SENS:FREQ:STOP 200e6;*OPC?\n'
s.send(MESSAGE)
()
MESSAGE = 'SENS:SWE:POIN 151;*OPC?\n'
s.send(MESSAGE)

MESSAGE = 'BWID 300;*OPC?\n'
s.send(MESSAGE)

MESSAGE = 'AVER:COUN 1;*OPC?\n'
s.send(MESSAGE)

MESSAGE = 'INIT:CONT 0;*OPC?\n'
s.send(MESSAGE)

MESSAGE = 'SOUR:POW:ALC HIGH;*OPC?\n'
s.send(MESSAGE)

# Set internal memory as place to store data
MESSAGE = 'MMEM:CDIR "[INTERNAL]:";*OPC?\n'
s.send(MESSAGE)

time.sleep(10)



#### Labjack ####

# Opening device
d = u3.U3()

# Channels 4-7 digital. 0-3 analog.
d.configU3(FIOAnalog = 15)      
d.configIO(FIOAnalog = 15)

# Inverse logic, all outputs OFF
d.setDOState(4, state = 1)      
d.setDOState(5, state = 1)
d.setDOState(6, state = 1)
d.setDOState(7, state = 1)






############ Continuous Measurements ##############
print " "
print 'STARTING MEASUREMENTS'


run = 0
while True:

	run = run + 1

	#### Reading and saving temperature and humidity voltages ####

	# Reading from Labjack
	VTbox = d.getAIN(0) # voltage from thermistor in front-end box
        VHant = d.getAIN(2) # voltage from humidity sensor in weather station
        VTant = d.getAIN(3) # voltage from thermistor in weather station

	# Opening file for appending, and saving
	with open(FILE_VOLTAGE, "a") as v:
		text_string = time.strftime("%Y%m%d") + " " + time.strftime("%H%M%S") + " " + str(VTbox) + " " + str(VHant) + " " + str(VTant)
        	if run == 1:
        		v.write(text_string)
        	elif run > 1:
        		v.write('\n' + text_string)





	#### INPUT 1 ####

	# Activating OPEN with Labjack 
	d.setDOState(4, state = 0)
	d.setDOState(5, state = 1)
	d.setDOState(6, state = 1)
	d.setDOState(7, state = 0)
	time.sleep(2)


	# Measure and save trace
	MESSAGE = 'INIT:IMM;*OPC?\n'

	print '_____________________________________________________'
	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	print time_now + ' ---- RUN ' + str(run) + ': Measuring Input 1 ...'
 
	s.send(MESSAGE)
	time.sleep(3)
 
	MESSAGE = 'MMEM:STOR:SNP "' + FILE_VNA + '";*OPC?\n'
	s.send(MESSAGE)
	time.sleep(3)  # This command is mandatory for the file to be saved

	# Send file to PC
	FILE_PC        = 'run_' + str(run).zfill(4) + "_input1_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + '.s1p'

	ftp = ftplib.FTP(TCP_IP)
	ftp.login("anonymous", "a@b.cd")

	ftp.cwd('\UserData')  # Root folder of VNA                  
	ftp.retrbinary('RETR %s' % FILE_VNA, open(DATA_FOLDER_PC + FILE_PC, 'wb').write)
	ftp.delete(FILE_VNA)
	ftp.quit()
                      




	#### INPUT 2 ####

	# Activating SHORT with Labjack 
	d.setDOState(4, state = 1)
	d.setDOState(5, state = 0)
	d.setDOState(6, state = 1)                                                                         
	d.setDOState(7, state = 0)
	time.sleep(2)


	# Measure and save trace
	MESSAGE = 'INIT:IMM;*OPC?\n'

	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	print time_now + ' ---- RUN ' + str(run) + ': Measuring Input 2 ...'
 
	s.send(MESSAGE)
	time.sleep(3)
 
	MESSAGE = 'MMEM:STOR:SNP "' + FILE_VNA + '";*OPC?\n'
	s.send(MESSAGE)
	time.sleep(3)  # This command is mandatory for the file to be saved


	# Send file to PC
	FILE_PC        = 'run_' + str(run).zfill(4) + "_input2_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + '.s1p'

	ftp = ftplib.FTP(TCP_IP)
	ftp.login("anonymous", "a@b.cd")

	ftp.cwd('\UserData')  # Root folder of VNA
	ftp.retrbinary('RETR %s' % FILE_VNA, open(DATA_FOLDER_PC + FILE_PC, 'wb').write)
        ftp.delete(FILE_VNA)
	ftp.quit()



	#### INPUT 3 ####

	# Activating MATCH with Labjack 
	d.setDOState(4, state = 1)
	d.setDOState(5, state = 1)
	d.setDOState(6, state = 0)
	d.setDOState(7, state = 0)
	time.sleep(2)


	# Measure and save trace
	MESSAGE = 'INIT:IMM;*OPC?\n'

	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	print time_now + ' ---- RUN ' + str(run) + ': Measuring Input 3 ...'
 
	s.send(MESSAGE)
	time.sleep(3)
 
	MESSAGE = 'MMEM:STOR:SNP "' + FILE_VNA + '";*OPC?\n'
	s.send(MESSAGE)
	time.sleep(3)  # This command is mandatory for the file to be saved

	
	# Send file to PC
	FILE_PC        = 'run_' + str(run).zfill(4) + "_input3_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + '.s1p'

	ftp = ftplib.FTP(TCP_IP)
	ftp.login("anonymous", "a@b.cd")

	ftp.cwd('\UserData')  # Root folder of VNA
	ftp.retrbinary('RETR %s' % FILE_VNA, open(DATA_FOLDER_PC + FILE_PC, 'wb').write)
        ftp.delete(FILE_VNA)
	ftp.quit()





	#### INPUT 4 ####

	# Activating ANTENNA with Labjack
	d.setDOState(4, state = 1)      
	d.setDOState(5, state = 1)
	d.setDOState(6, state = 1)
	d.setDOState(7, state = 0)
	time.sleep(2)


	# Measure and save trace
	MESSAGE = 'INIT:IMM;*OPC?\n'

	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	print time_now + ' ---- RUN ' + str(run) + ': Measuring Input 4 ...'
 
	s.send(MESSAGE)
	time.sleep(3)
 
	MESSAGE = 'MMEM:STOR:SNP "' + FILE_VNA + '";*OPC?\n'
	s.send(MESSAGE)
	time.sleep(3)  # This command is mandatory for the file to be saved


	# Send file to PC
	FILE_PC        = 'run_' + str(run).zfill(4) + "_input4_" + time.strftime("%Y%m%d") + "_" + time.strftime("%H%M%S") + '.s1p'

	ftp = ftplib.FTP(TCP_IP)
	ftp.login("anonymous", "a@b.cd")

	ftp.cwd('\UserData')  # Root folder of VNA
	ftp.retrbinary('RETR %s' % FILE_VNA, open(DATA_FOLDER_PC + FILE_PC, 'wb').write)
        ftp.delete(FILE_VNA)
	ftp.quit()





	#### Turn OFF, and kill time (28 s) to complete 1 minute ####
	
	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	print time_now + ' ---- RUN ' + str(run) + ': Waiting for next cycle ...'

	d.setDOState(4, state = 1)      
	d.setDOState(5, state = 1)
	d.setDOState(6, state = 1)
	d.setDOState(7, state = 1)
	time.sleep(28)               # This completes 1 minute, since the four measurements take 32 seconds. 



s.close()















