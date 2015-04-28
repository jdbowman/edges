#!/usr/bin/python

import edges
import getopt
import sys
from datetime import datetime

def checkThermal(argv):
  """
  Read the thermal controller
  """
  
  # Set default parameter values
  result = True
  bSave = False
  helpString =  '\nusage: checkThermal.py [options]\n\n' \
                '\tRead the thermal controller and print the\n' \
                '\tvalues to stdout.\n\n' \
                '\tOptions:\n' \
                '\t-h, --help:\t show this page\n' \
                '\t-s, --save:\t write the values to the record file\n' \
                '\t-t, --set:\t send settings to the thermal controller\n'

  # Parse the commnd line arguments
  try:
    opts, args = getopt.getopt(argv,'hst',['help','save', 'set'])
  except getopt.GetoptError:
    print(helpString)
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
       print(helpString)
       sys.exit()
    elif opt in ('-s', '--save'):
       bSave = True
    elif opt in ('-t', '--set'):
       bSet = True

  # Get an instance of the EDGES class
  d = edges.edges()

  # Get the command dictionary
  thermal_cmds = d.getThermalDictionary()

  # Open connection to thermal controller
  connection = d.openThermalConnection()
  if not connection:
    print('Abort.  No connection to thermal controller.')
    return False

  responses = {}

  # Loop over all commands in dictionary
  for key in sorted(thermal_cmds):

    # Only send the "read" commands
    if key.startswith('read'):
      
      # Store and print the response values
      value = d.sendThermalCommand(key, connection=connection)
      unit = thermal_cmds[key][2]
      responses[key] = (value, unit)
      print("{}: {:.2f} {}".format(key.rjust(25), value, unit))
 
  # Save the data if desired
  if bSave:

    # Concatenate label text and units for the subset of data we actually
    # want to save
    saveKeys = ('read_temp_set', 'read_input1', 'read_power')
    saveValues = [responses[key][0] for key in saveKeys]
    fullLabels = ["{} [{}]".format(key[5:], responses[key][1]) for key in saveKeys]

    # Write to EDGES file record
    result = d.writeRecord( 'thermal', 'thermal', 
                            datetime.utcnow(), saveValues, 
                            fullLabels, breaklevel=2)

  if bSet:

    # Update the thermal controller settings based on the EDGES configuration
    # file settings
    setKeys = ( 'set_temp', 'set_voltage', 'set_bandwidth', 
                'set_gain', 'set_derivative', 'set_outpu_enabled' )

    for key in setKeys:

      setValue = d.settings.get('Thermal', key)
      response = d.sendThermalCommand(key, arg=setValue, connection=connection)
      unit = thermal_cmds[key][2]

      print("{}: {:.2f} {} : respond = {}".format(key.rjust(25), setValue, unit, response))
      


  return True
  
   


if __name__ == "__main__":
  checkThermal(sys.argv[1:])
