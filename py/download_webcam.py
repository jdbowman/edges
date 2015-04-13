#!/usr/bin/python

import time
import urllib2

##############################################################
### download_webcam.py                                     ###    
###                                                        ###
### Retrieves the ASKAP webcam webpage, identifies the URL ###
### of the latest webcam image and downloads the image     ###
### into the EDGES_data/webcam directory.  This script is  ###
### intended to be called from crontab on a regular basis  ###
### so we a have a general visual record of the conditions ###
### at the MRO.                                            ###
##############################################################

# Set the EDGES output directory
strdir = "/media/DATA/EDGES_data/webcam/"

# Download webcam page
url = "http://www.atnf.csiro.au/projects/askap/webcam/"
page = urllib2.urlopen(url)
data = page.read()

# Search for latest image URL
str = "camera_1/gnomecam_"
strlen = len(str)
index = data.find(str)

# Create a file name using the current date and time
strfile = time.strftime("%Y_%j_%H_%M_camera_1.jpg")

# Open latest image
imgind = index+strlen
imgurl = "http://www.atnf.csiro.au/projects/askap/webcam/" + str + data[imgind:imgind+8]
imgpage = urllib2.urlopen(imgurl)

# Retrieve image into file
file = open(strdir + strfile, "wb")
file.write(imgpage.read())
file.close

