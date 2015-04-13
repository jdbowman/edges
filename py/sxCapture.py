#!/usr/bin/python

import usb.util
import usb.core
import sys
import time
import numpy as np
import struct
from array import array
from PIL import Image

#####################################################
# Connect to the camera
#####################################################
def connect():

	# Here is the hard-coded SX camera product ID
	sxProductID = 0x0509;

	# Look for the camera on USB
	dev = usb.core.find(idProduct=sxProductID)

	# Abort if we didn't find the camera
	if dev is None:
		return None;

	print (usb.util.get_string(dev, dev.iManufacturer))
	print (usb.util.get_string(dev, dev.iProduct))

	# Set the active configuration. With no arguments, the first
	# configuration will be the active one
	dev.set_configuration()

	# Get an endpoint instance
	cfg = dev.get_active_configuration()
	interface = cfg[(0,0)]

	ep = usb.util.find_descriptor(
		  interface,
		  # match the first OUT endpoint
		  custom_match = \
		  lambda e: \
		      usb.util.endpoint_direction(e.bEndpointAddress) == \
		      usb.util.ENDPOINT_OUT)

	dev.reset()
	return dev;

#####################################################
# get_firmware_version 
#####################################################
def get_firmware_version(dev):
	
	commandblock = array('B', [64, 255, 0, 0, 0, 0, 0, 0])
	print (commandblock)

	length = dev.write(0x01, commandblock)	
	assert length == len(commandblock)

	readblock = dev.read(0x82, 4)
	assert len(readblock) == 4

	version = "%d.%d" % (readblock[2] | (readblock[3] << 8), readblock[0] | readblock[1])

	return version


#####################################################
# Dump the charge in all pixels
#####################################################
def dump_charge(dev):

	id = 0
	commandblock = array('B', [64, 1, 0, 0, id, 0, 0, 0])

	length = dev.write(0x01, commandblock, 100)
	assert length == len(commandblock)


#####################################################
# get_row_data (CMD: 3)
#####################################################
def get_row_data (dev, x, y, x_wid, y_wid, x_bin, y_bin) :

	id = 0
	nread = 2 * x_wid * y_wid
	rows = 3 # odd = 1, even = 2, all = 3
	commandblock = array('B', [64, 3, rows, 0, id, 0, 10, 0, 
														x & 0xFF, x >> 8, y & 0xFF, y >> 8, 
														x_wid & 0xFF, x_wid >> 8, y_wid & 0xFF, y_wid >> 8,
							 							x_bin, y_bin])

	length = dev.write(0x01, commandblock, 100)	
	assert length == len(commandblock)

	data = dev.read(0x82, nread)

	return data


#####################################################
# Get camera info
#####################################################
def get_camera_info (dev):

	id = 0
	commandblock = array('B', [192, 14, 0, 0, id, 0, 2, 0])
	length = dev.write(0x01, commandblock)	
	assert length == len(commandblock)
	nread = 2
	readblock = dev.read(0x82, nread)
	assert len(readblock) == nread

	print (readblock)
	
	modnum = readblock[0] | (readblock[1] << 8);
	print (modnum); # Camera modnum (must contain a bunch bits that encode info)
	
	# Interlaced...
	bIsInterlaced = modnum & 0x40
	if (modnum == 0x84): 
		bIsInterlaced = 1
	modnum &= 0x1F
	if ( (modnum == 0x16) or (modnum == 0x17) or (modnum == 0x18) or (modnum == 0x19)):
		bIsInterlaced = 0;
	
	# Color...
	bIsColor = readblock[0] & 0x80

	print (bIsInterlaced)
	print (bIsColor)
	
	# --- Now ask about CCD parameters ---
	commandblock = array('B', [64, 8, 0, 0, id, 0, 17, 0])
	length = dev.write(0x01, commandblock)	
	assert length == len(commandblock)
	nread = 17
	readblock = dev.read(0x82, nread)
	assert len(readblock) == nread
	
	print (readblock)

	# Chip size in pixels...
	max_h = readblock[2] | (readblock[3] << 8)
	max_v = readblock[6] | (readblock[7] << 8)
	if (bIsInterlaced):
		max_v *= 2
	
	# Pixel size in microns...
	pixsiz_h = (readblock[8] | (readblock[9] << 8)) / 256.0
	pixsiz_v = (readblock[10] | (readblock[11] << 8)) / 256.0
	if (bIsInterlaced):
		pixsiz_v /= 2
	
	# Bits per pixel and max adu value per pixel...
	bitspp = readblock[14]
	max_adu = (1 << readblock[14]) - 1
	
	# Pulse guide...
	bCanPulseGuide = readblock[16] & 0x01
	
	# Cooler...
	bCanSetCCDTemp = readblock[16] & 0x10

	# Shutter...
	bHasShutter = readblock[16] & 0x20
	
	print (max_h)
	print (max_v)
	



#####################################################
#####################################################
# Execute
#####################################################
#####################################################

dev = connect()
get_firmware_version(dev)
get_camera_info(dev)

dump_charge(dev)
time.sleep(2.0)
data = get_row_data(dev, 0, 0, 1392, 1040, 1, 1)
print(len(data))

data_shorts = struct.unpack('%sH' % (len(data)/2), data)
data_reshape = np.array(data_shorts).reshape(1040, 1392)
print (data_reshape.dtype)
print(data_reshape)


image = Image.fromarray(data_reshape.astype(np.int32))
image.save('out.png')













