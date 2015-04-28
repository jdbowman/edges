import usb.util
import usb.core
import sys
import time
import numpy as np
import struct
from array import array
from PIL import Image


#######################################################
#
# cameraSX
#
# Class that provides basic communication functions
# to Starlight Xpress CCD cameras
#
# This is based on the SX example code posted on the
# sxccd.com website.  
#
#######################################################

class cameraSX:
	"""Communicate with Starlight Xpress CCD cameras"""
	
	SX_VENDOR_ID 							=	0x1278
	SX_PRODUCT_ID_OCULUS			= 0x0509	# Oculus all-sky camera

	USB_ENDPOINT_OUT 					=	0x01
	USB_ENDPOINT_IN 					=	0x82

	CCD_FLAGS_FIELD_ODD				=	0x01		# Specify odd field for MX cameras
	CCD_FLAGS_FIELD_EVEN      =	0x02		# Specify even field for MX cameras
	CCD_FLAGS_NOBIN_ACCUM     =	0x04		# Don't accumulate charge if binning
	CCD_FLAGS_NOWIPE_FRAME    =	0x08		#	Don't apply WIPE when clearing frame
	CCD_FLAGS_TDI             =	0x20		#	Implement TDI (drift scan) operation
	CCD_FLAGS_NOCLEAR_FRAME   =	0x40		#	Don't clear frame, even when asked


	#####################################################
	# __init__
	#####################################################
	def __init__(self):
		
		self.device = None
		self.manufacturerString = ""
		self.productString = ""

		

	#####################################################
	# connect
	#####################################################
	def connect(self, productId=None):

		# Look for the camera on USB
		# If a productId is specified, look for that specific type of camera, 
		# otherwise look for an SX device connected by USB
		if (productId):
			self.device = usb.core.find(idVendor=self.SX_VENDOR_ID, 
																	idProduct=productId)
		else:
			self.device = usb.core.find(idVendor=self.SX_VENDOR_ID)

		# Abort if we didn't find the camera
		if self.device is None:
			return False

		# Reset the device in case it was left in a funky state
		self.device.reset()

		# Read and store USB device information
		self.manufacturerString = usb.util.get_string(
																self.device, self.device.iManufacturer)
		self.productString = usb.util.get_string(
																self.device, self.device.iProduct)

		# Set the active configuration. With no arguments, the first
		# configuration will be the active one
		self.device.set_configuration()

		# Get an endpoint instance
		#cfg = self.device.get_active_configuration()
		#interface = cfg[(0,0)]

		return True


	#####################################################
	# captureImage
	#####################################################
	def captureImage( self, x_offset, y_offset, width, height, 
									  x_bin, y_bin, exposureDuration):
		
		if (exposureDuration < 5000):
			# use readPixelsDelayed
			pixels = self.readPixelsDelayed( x_offset, y_offset, 
																				width, height, x_bin, y_bin, 
																				exposureDuration)
		else:
			# do it manually
			self.clearPixels()
			time.sleep(exposureDuration / 1000.0)
			pixels = self.readPixels(x_offset, y_offset, width, height, x_bin, y_bin)

		assert pixels

		# Raw byte pairs are actually little endian unsigned short values
		# Here, we convert the raw bytes to integers
		pixels = struct.unpack('%sH' % (len(pixels)/2), pixels)

		# Put the pixels into a numpy array so we can reshape it into
		# the proper dimensions of the image
		pixels = np.array(pixels).reshape(height, width)

		# Convert to an image
		# image = Image.fromarray(pixels.astype(np.int32))

		return pixels

	

		


	#####################################################
	# clearPixels (CMD: 1)
	#####################################################
	def clearPixels(self, chip_id=0):

		assert self.device

		commandblock = array('B', [64, 1, 0, 0, chip_id, 0, 0, 0])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)
		assert length == len(commandblock)


	#####################################################
	# readPixelsDelayed (CMD: 2)
	#####################################################
	def readPixelsDelayed ( self, 
									x_offset, y_offset, 
									width, height, 
									x_bin, y_bin, 
									exposure,
									flags=CCD_FLAGS_FIELD_ODD | CCD_FLAGS_FIELD_EVEN, 
									chip_id=0):

		# From SX: "An implied CLEAR_PIXELS is done at the 
		# beginning of the exposure.  All of the CLEAR_PIXELS 
		# flags are in effect."

		# The EXPOSURE argument is in milliseconds
		# The FLAGS argument can be combination of CCD_FLAGS_*		

		assert self.device

		delay = int(exposure)

		commandblock = array('B', [64, 2, flags, 0, chip_id, 0, 10, 0, 
															x_offset & 0xFF, x_offset >> 8, 
															y_offset & 0xFF, y_offset >> 8, 
															width & 0xFF, width >> 8, 
															height & 0xFF, height >> 8,
								 							x_bin, y_bin,
															(delay & 0xFF), (delay & 0xFF00) >> 8, 
															(delay & 0xFF0000) >> 16, (delay & 0xFF000000) >> 24])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)	
		assert length == len(commandblock)

		time.sleep(delay / 1000.0)

		pixels_per_row = int(width / x_bin)
		pixels_per_col = int(height / y_bin)

		nread = 2 * pixels_per_row * pixels_per_col
		readblock = self.device.read(self.USB_ENDPOINT_IN, nread)
		assert len(readblock) == nread

		return readblock


	#####################################################
	# readPixels (CMD: 3)
	#####################################################
	def readPixels( self, 
									x_offset, y_offset, 
									width, height, 
									x_bin, y_bin, 
									flags=CCD_FLAGS_FIELD_ODD | CCD_FLAGS_FIELD_EVEN,
									chip_id=0 ):

		# The FLAGS argument can be any combination of: FIELD_EVEN, 
		# FIELD_ODD, NOBIN_ACCUM, and TDI

		commandblock = array('B', [64, 3, flags, 0, chip_id, 0, 10, 0, 
															x_offset & 0xFF, x_offset >> 8, 
															y_offset & 0xFF, y_offset >> 8, 
															width & 0xFF, width >> 8,
															height & 0xFF, height >> 8,
								 							x_bin, y_bin])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)	
		assert length == len(commandblock)

		pixels_per_row = int(width / x_bin)
		pixels_per_col = int(height / y_bin)

		nread = 2 * pixels_per_row * pixels_per_col
		readblock = self.device.read(self.USB_ENDPOINT_IN, nread)
		assert len(readblock) == nread

		return readblock


	#####################################################
	# reset (CMD: 6)
	#####################################################
	def reset(self):

		assert self.device

		commandblock = array('B', [64, 6, 0, 0, 0, 0, 0, 0])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)	
		assert length == len(commandblock)


	#####################################################
	# getCCDParams (CMD: 8)
	#####################################################
	def getCCDParams(self, chip_id=0):
	
		assert self.device

		commandblock = array('B', [64, 8, 0, 0, chip_id, 0, 17, 0])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)	
		assert length == len(commandblock)

		nread = 17
		readblock = self.device.read(self.USB_ENDPOINT_IN, nread)
		assert len(readblock) == nread
	
		# Parse parameters as best we can
		params = dict()
		params['HFRONT_PORCH'] = readblock[0]
		params['HBACK_PORCH'] = readblock[1]
		params['WIDTH'] = readblock[2] | (readblock[3] << 8)
		params['VFRONT_PORCH'] = readblock[4]
		params['VBACK_PORCH'] = readblock[5]
		params['HEIGHT'] = readblock[6] | (readblock[7] << 8)
		params['PIXEL_WIDTH'] = (readblock[8] | (readblock[9] << 8)) / 256.0
		params['PIXEL_HEIGHT'] = (readblock[10] | (readblock[11] << 8)) / 256.0
		params['COLOR_MATRIX'] = (readblock[12] | (readblock[13] << 8))
		params['BITS_PER_PIXEL'] = readblock[14]
		params['NUM_SERIAL_PORTS'] = readblock[15]
		params['EXTRA_CAPABILITIES'] = readblock[16]

		# Parse extra capabilities (this is only a subset)
		params['EXTRA_STAR2000_PORT'] = readblock[16] & 0x01
		params['EXTRA_EEPROM'] = (readblock[16] & 0x04) >> 2
		params['EXTRA_INTEGRATED_GUIDER_CCD'] = (readblock[16] & 0x08) >> 3
		params['EXTRA_CCD_TEMPERATURE_CONTROL'] = (readblock[16] & 0x10) >> 15
		params['EXTRA_CCD_SHUTTER'] = (readblock[16] & 0x20) >> 31

		return params


	#####################################################
	# cameraModel (CMD: 14)
	# 
	# Returns model number from camera.  Older cameras do
	# not have model number defined.  Here are some of the
	# model numbers listed by SX.
	# 0x09		 HX9
	# 0x45   	 MX5
	# 0xC5   	 MX5C
	# 0x47		 MX7
	# 0xC7		 MX7C
	# 0x49   	 MX9
	# 0xFFFF	 Undefined camera model
	#####################################################
	def cameraModel(self):

		assert self.device

		commandblock = array('B', [192, 14, 0, 0, 0, 0, 2, 0])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)	
		assert length == len(commandblock)

		nread = 2
		readblock = self.device.read(self.USB_ENDPOINT_IN, nread)
		assert len(readblock) == nread
	
		model = readblock[0] | (readblock[1] << 8);
		
		return model

	
	#####################################################
	# firmwareVersion (CMD: 255)
	#####################################################
	def firmwareVersion(self):

		assert self.device

		commandblock = array('B', [64, 255, 0, 0, 0, 0, 0, 0])
		length = self.device.write(self.USB_ENDPOINT_OUT, commandblock)	
		assert length == len(commandblock)

		nread = 4
		readblock = self.device.read(self.USB_ENDPOINT_IN, nread)
		assert len(readblock) == nread

		version = "%d.%d" % (readblock[2] | (readblock[3] << 8), 
			readblock[0] | readblock[1])

		return version








