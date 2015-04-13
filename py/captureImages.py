#!/usr/bin/python

import cameraSX
import numpy as np
import struct
from array import array
from PIL import Image
from subprocess import call
from datetime import datetime
import time
import urllib2


##############################################################
### main()			 																					 ###
###																												 ###
### The primary script - it is run after all function      ###
### definitions have occurred.	                  				 ###
##############################################################
def main():

	datadir = "/home/loco/edges/data/cameras/"
	datestr = datetime.strftime(datetime.utcnow(), "%Y_%j_%H_%M")

	TIME_FLAGS_NIGHT = 0
	TIME_FLAGS_TWILIGHT = 1
	TIME_FLAGS_DAYTIME = 2
	iTimeFlag = TIME_FLAGS_NIGHT
	local_hour = (datetime.utcnow().hour + 8) % 24
	if (local_hour > 5):
		iTimeFlag = TIME_FLAGS_TWILIGHT
	if (local_hour > 9):
		iTimeFlag = TIME_FLAGS_DAYTIME
	if (local_hour> 5):
		iTimeFlag = TIME_FLAGS_TWILIGHT
	if (local_hour > 9):
		iTimeFlag = TIME_FLAGS_NIGHT

	print local_hour
	print iTimeFlag

	# Capture image from ASKAP webcam (camera_1)
	getASKAPCamera(datadir + datestr + "_camera_1.jpg", iTimeFlag)

	# Capture image from local USB camera (camera_2)
	getUSBCamera(datadir + datestr + "_camera_2.png", iTimeFlag)
	
	# Capture image from all-sky camera (camera_3)
	getSXCamera(datadir + datestr + "_camera_3.png", iTimeFlag)



##############################################################
### getASKAPCamera()                                       ###    
###                                                        ###
### Retrieves the ASKAP webcam webpage, identifies the URL ###
### of the latest webcam image and downloads the image     ###
### into the EDGES_data/webcam directory.  This script is  ###
### intended to be called from crontab on a regular basis  ###
### so we a have a general visual record of the conditions ###
### at the MRO.                                            ###
##############################################################
def getASKAPCamera(filename, iTimeFlag):

	# Download webcam page
	url = "http://www.atnf.csiro.au/projects/askap/webcam/"
	page = urllib2.urlopen(url)
	data = page.read()

	# Search for latest image URL
	str = "camera_1/gnomecam_"
	strlen = len(str)
	index = data.find(str)

	# Open latest image
	imgind = index+strlen
	imgurl = "http://www.atnf.csiro.au/projects/askap/webcam/" + str + data[imgind:imgind+8]
	imgpage = urllib2.urlopen(imgurl)

	# Retrieve image into file
	file = open(filename, "wb")
	file.write(imgpage.read())
	file.close



##############################################################
### getUSBCamera()                                         ###    
###                                                        ###
### Retrieves the USB webcam image using ffmpeg.					 ###
##############################################################
def getUSBCamera(filename, iTimeFlag):

	call(['ffmpeg', 
				'-f', 'video4linux2', 
				'-s', '1920x1080', 
				'-i', '/dev/video0', 
				'-vframes', '30', 
				'-f', 'null'
				'/dev/null'])

	call(['ffmpeg', 
				'-f', 'video4linux2', 
				'-s', '1920x1080', 
				'-i', '/dev/video0', 
				'-vframes', '1', 
				filename])



##############################################################
### getSXCamera()                                          ###    
###                                                        ###
### Retrieves the all-sky webcam image.         					 ###
##############################################################
def getSXCamera(filename, iTimeFlag):
	sx = cameraSX.cameraSX()
	if not (sx.connect(sx.SX_PRODUCT_ID_OCULUS)):
		print ("Failed to connect to all-sky camera!")
	else:
		print ("Connected to all-sky camera.")

		sx.reset()
		params = sx.getCCDParams()
		width = params['WIDTH']
		height = params['HEIGHT']

		exposure = 500	
		target = 2**13
		threshold = 0.1
		ratio = 0.5
		max_exposure = 120000
		min_exposure = 1
		counter = 0
		while ( (abs(ratio - 1) > threshold) and (exposure<max_exposure) and (counter < 5)): 

			counter += 1
			exposure /= ratio

			if (exposure > max_exposure):
				exposure = max_exposure
			elif (exposure < min_exposure):
				exposure = min_exposure
		
			print ("Capturing image (exposure: %d ms)..." % exposure)
			pixels = sx.captureImage(0, 0, width, height, 1, 1, exposure)
			median = np.median(pixels[250:750,400:900])
			ratio = (median-1500) / target
			print ("counter: %d median: %6.2f  target: %6.2f  ratio: %6.2f  diff: %6.2f" % 
							(counter, median, target, ratio, abs(ratio-1)))

		print ("Saving imaging to %s" % filename)
		image = Image.fromarray(pixels.astype(np.int32))
		image.save(filename)



##############################################################
### Run the script!                                        ###
##############################################################
main()






