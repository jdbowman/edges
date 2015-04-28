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
  bUpdate = False
  bLimit = False
  bLimitExceeded = False
  helpString =  '\nusage: checkThermal.py [options]\n\n' \
                '\tRead the thermal controller and print the\n' \
                '\tvalues to stdout.\n\n' \
                '\tOptions:\n' \
                '\t-h, --help:\t show this page\n' \
                '\t-l, --limit:\t enforce the power-off thermal limit\n' \
                '\t-s, --save:\t write the values to the record file\n' \
                '\t-u, --update:\t update settings on the thermal controller\n' \
                '\n\t Uses the Thermal settings from the EDGES .ini file\n'

  # Parse the commnd line arguments
  try:
    opts, args = getopt.getopt(argv,'hlsu',['help','limit','save', 'update'])
  except getopt.GetoptError:
    print(helpString)
    return False

  for opt, arg in opts:
    if opt in ('-h', '--help'):
       print(helpString)
       sys.exit()
    elif opt in ('-l', '--limit'):
       bLimit = True
    elif opt in ('-s', '--save'):
       bSave = True
    elif opt in ('-u', '--update'):
       bUpdate = True

  # Get an instance of the EDGES class
  d = edges.edges()

  # Get the command dictionary
  thermal_cmds = d.getThermalDictionary()

  # Open connection to thermal controller
  connection = d.openThermalConnection()
  if not connection:
    print('Abort.  No connection to thermal controller.')
    return False

  print('\nReading thermal controller status...\n')

  # Loop over all commands in dictionary
  responses = {}
  for key in sorted(thermal_cmds):

    # Only send the "read" commands
    if key.startswith('read'):
      
      # Store and print the response values
      value = d.sendThermalCommand(key, connection=connection)
      unit = thermal_cmds[key][2]
      responses[key] = (value, unit)
      print("{}: {:.2f} {}".format(key.rjust(25), value, unit))
 
  print('')

  # If the save option is set, store the basic readouts to a record a file
  if bSave:

    print('Saving record...')

    # Read the installation settings
    site = d.settings.get('Installation', 'site')
    instrument = d.settings.get('Installation', 'instrument')
    name = d.settings.get('Thermal', 'output_name')

    # Concatenate label text and units for the subset of data we actually
    # want to save
    saveKeys = ('read_temp_set', 'read_input1', 'read_power')
    saveValues = [responses[key][0] for key in saveKeys]
    fullLabels = ["{} [{}]".format(key[5:], responses[key][1]) for key in saveKeys]

    # Write to EDGES file record
    result = d.writeRecord( '{}/{}/{}'.format(site, instrument, name), name, 
                            datetime.utcnow(), saveValues, 
                            fullLabels, breaklevel=2)

    if result:
      print ('Success.\n')
    else:
      print ('Failed.\n')


  # If the thermal limit option is set, then turn off the receiver whenever the
  # the thermal controller reports a high temperature above the specified limit.
  if bLimit:

    currentTemp = responses['read_input1'][0]
    currentUnit = responses['read_input1'][1]
    limitTemp = float(d.settings.get('Thermal', 'power_off_temp'))

    print('Checking thermal limit...')
    print('Current temperature is {:.2f} {}'.format(currentTemp, currentUnit))
    print('Limit temperature is {:.2f} {}'.format(limitTemp, currentUnit)) 

    if (currentTemp > limitTemp):
      
      print('WARNING!  Current temperature exceeded limit.')

      bLimitExceeded = True

      # Get receiver outlet from settings
      receiverOutlet = int(d.settings.get('Power', 'receiver_outlet'))

      # Send the power switch command to turn off the receiver power
      if (d.setOutlet(receiverOutlet, 0)):
        print('Successfully turned off receiver (outlet: {})'.format(receiverOutlet))
      else:
        print('Failed to turn off receiver (outlet: {})'.format(receiverOutlet))

    print('')

  # If the update option is set, update the thermal controller settings based on 
  #the EDGES configuration settings
  if bUpdate:

    print('Updating onboard thermal controller settings...\n')

    setKeys = [ 'set_temp', 'set_voltage', 'set_bandwidth', 
                'set_gain', 'set_derivative' ]

    # If the thermal limit was exceeded (and enforced) above, then don't turn
    # the thermal controller back on.  So only include output_enabled setting
    # if the thermal limit was not exceeded.
    if not bLimitExceeded:
      setKeys.append('set_output_enabled')
    
    for key in setKeys:

      setValue = float(d.settings.get('Thermal', key))
      response = d.sendThermalCommand(key, arg=setValue, connection=connection)
      unit = thermal_cmds[key][2]

      print("{}: {:.2f} {} : response = {}".format( key.rjust(25), setValue, 
                                                    unit, response ))

    print('')

  return True
  
   


if __name__ == "__main__":
  checkThermal(sys.argv[1:])
