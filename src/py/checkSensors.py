#!/usr/bin/python

import edges
import getopt
import socket
import sys
from datetime import datetime

def checkConduit(argv):
  """
  Read the conduit sensors if they are connected to this host and print the values
  to stdout.
  """
  
  # Set default parameter values
  result = True
  bSave = False
  helpString =  '\nusage: checkConduit.py [options]\n\n' \
                '\tRead the conduit sensors if they are connected\n' \
                '\tto this host and print the values to stdout.\n\n' \
                '\tOptions:\n' \
                '\t-h, --help:\t show this page\n' \
                '\t-s, --save:\t write the values to the record file\n'

  # Parse the commnd line arguments
  try:
    opts, args = getopt.getopt(argv,'hs',['help','save'])
  except getopt.GetoptError:
    print(helpString)
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
       print(helpString)
       sys.exit()
    elif opt in ('-s', '--save'):
       bSave = True

  # Abort if we are on the wrong host to check conduit sensors
#  if socket.gethostname() != 'edges-pc-low':
#    
#    print('ERROR: This host is not connected to the conduit sensors.  Aborted.')
#    return False

  # Check the sensors
#  else:
  if (True):
    # Get an instance of the EDGES class
    d = edges.edges()

    # Read the environment sensors
    values = d.getEnvironmentSensors()

    # Read the sensor labels from the EDGES settings
    labels = (  d.settings.get('Environment', 'sensor1_label'),
                d.settings.get('Environment', 'sensor2_label'),
                d.settings.get('Environment', 'sensor3_label'),
                'Rack Temperature' )

    # Read the sensor units from the EDGES settings
    units = ( d.settings.get('Environment', 'sensor1_unit'),
              d.settings.get('Environment', 'sensor2_unit'),
              d.settings.get('Environment', 'sensor3_unit'),
              'K' )
    
    # Read the installation settings
    site = d.settings.get('Installation', 'site')
    instrument = d.settings.get('Installation', 'instrument')
    name = d.settings.get('Environment', 'output_name')

    print('\nReading environmental sensor data...\n')

    # Print the labels and values to stdout
    for l, v, u in zip(labels, values, units):
      print("{}: {:.2f} {}".format(l.rjust(25), v, u))

    print('')

    # Save the data if desired
    if bSave:

      print('Saving record...')

      # Concatenate label text and units
      fullLabels = ["{} [{}]".format(l, u) for l, u in zip(labels, units)]

      # Write to EDGES file record
      result = d.writeRecord( '{}/{}'.format(site, name), name, 
                              datetime.utcnow(), values, 
                              fullLabels, breaklevel=2)

      if result:
        print('Success.\n')
      else:
        print('Failed.\n')


    return result
    
   


if __name__ == "__main__":
  checkConduit(sys.argv[1:])
