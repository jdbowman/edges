#!/usr/bin/python

import edges
import getopt
import socket
import sys
from datetime import datetime

def powerOff(argv):
  """
  Turn off the power outlets for the receiver and thermal controller associated 
  with this instrument.
  """
  
  # Set default parameter values
  result1 = False
  result2 = False
  helpString =  '\nusage: powerOff.py\n\n' \
                '\tTurn off the power outlets for the receiver and thermal\n' \
                '\tcontroller associated with this instrument.\n\n' 

  # Parse the commnd line arguments
  try:
    opts, args = getopt.getopt(argv,'h',['help'])
  except getopt.GetoptError:
    print("Invalid argument.")
    print(helpString)
    return True

  for opt, arg in opts:
    if opt in ('-h', '--help'):
       print(helpString)
       return True

  # Get an instance of the EDGES class
  d = edges.edges()

  try:
    outlet_receiver = d.settings.get('Power', 'receiver_outlet')
    outlet_thermal = d.settings.get('Power', 'thermal_outlet')
  except:
    print ("Error.  Could not find configuration information for outlets.  Check the .ini file.\n")
    return False;

  print("Turning off outlets.")
  result1 = d.setOutlet(outlet_receiver, 0)
  result2 = d.setOutlet(outlet_thermal, 0)

  if (result1 & result2):
    print("Success.\n")
  elif (result1):
    print("Failed to turn off thermal outlet.\n")
  elif (result1):
    print("Failed to turn off receiver outlet.\n")
  else:
    print("Failed to turn off any outlets.\n")

  return (result1 & result2)
    
   


if __name__ == "__main__":
  powerOff(sys.argv[1:])

