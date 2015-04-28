#!/usr/bin/python

import edges
from datetime import datetime


def captureCameras():
  """
  Capture and store images from the three cameras used to monitor EDGES and its 
  site.
  """

  # Get an instance of the EDGES class
  d = edges.edges()

  # Define the output directory and file bases.
  subdir = 'cameras'
  datestr = datetime.strftime(datetime.utcnow(), "%Y_%j_%H_%M")
  pathbase = d.getDataDir() + '/' + subdir + '/' + datestr

  # Determine if it should be day or night time (for future use)
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

  # Capture image from ASKAP webcam (camera_1)
  print('Capturing ASKAP webcam...')
  d.getASKAPWebcam(pathbase + "_camera_1.jpg")

  # Capture image from local USB camera (camera_2)
  print('Capturing local USB camera...')
  d.getLocalUSBCamera(pathbase + "_camera_2.png")
  
  # Capture image from all-sky camera (camera_3)
  print('Capturing local all-sky camera...')
  d.getLocalSXCamera(pathbase + "_camera_3.png")

  print('Done.')



if __name__ == "__main__":
  captureCameras()





