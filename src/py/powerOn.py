#!/usr/bin/python

import edges
import getopt
import socket
import sys
from datetime import datetime

def powerOn(argv):
  """
  Turn on the power outlets for the receiver and thermal controller associated 
  with this instrument.
  """
  
  # Set default parameter values
  result1 = False
  result2 = False
  helpString =  '\nusage: powerOn.py\n\n' \
                '\tTurn on the power outlets for the receiver and thermal\n' \
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

  print("Turning on outlets.")
  result1 = d.setOutlet(outlet_receiver, 1)
  result2 = d.setOutlet(outlet_thermal, 1)

  if (result1 & result2):
    print("Success.\n")
  elif (result1):
    print("Failed to turn on thermal outlet.\n")
  elif (result1):
    print("Failed to turn on receiver outlet.\n")
  else:
    print("Failed to turn on any outlets.\n")

  return (result1 & result2)
    
   


if __name__ == "__main__":
  powerOn(sys.argv[1:])

