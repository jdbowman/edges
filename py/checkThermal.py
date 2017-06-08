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
  bEnable = False
  bDisable = False
  bSave = False
  bUpdate = False
  bLimit = False
  bLimitExceeded = False
  helpString =  '\nusage: checkThermal.py [options]\n\n' \
                '\tRead the thermal controller and print the values to \n' \
                '\tstdout.  Manage the settings of the controller.\n\n' \
                '\tOptions:\n' \
                '\t-d, --disable:\t Disable thermal controller output.\n' \
                '\t-e, --enable:\t Enable thermal controller output.  If --limit\n' \
                '\t\t\t is set and the current temperature exceeds the,\n' \
                '\t\t\t limit, the net result is to turn off the receiver,\n' \
                '\t\t\t but still enable the thermal controller.\n' \
                '\t-h, --help:\t Show this page\n' \
                '\t-l, --limit:\t Turn off receiver and disable controller output\n' \
                '\t\t\t if the temperature limit is exceeded.\n' \
                '\t-s, --save:\t Write readout values to record file\n' \
                '\t-u, --update:\t Update settings on the thermal controller\n' \
                '\n\t Uses the [Thermal] settings from the EDGES .ini file\n'

  # Parse the commnd line arguments
  try:
    opts, args = getopt.getopt( argv, 'dehlsu',
                                [ 'disable', 'enable', 'help','limit', 
                                  'save', 'update' ])
  except getopt.GetoptError:
    print('\nERROR: Invalid argument.\n\n{}'.format(helpString))
    return False

  for opt, arg in opts:
    if opt in ('-h', '--help'):
       print(helpString)
       return False
    elif opt in ('-d', '--disable'):
       bDisable = True
    elif opt in ('-d', '--enable'):
       bEnable = True
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
  connection = d.openThermalConnection('/dev/ttyUSB1')
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

    print('Saving record (--save)...')

    # Read the installation settings
    site = d.settings.get('Installation', 'site')
    instrument = d.settings.get('Installation', 'instrument')
    name = d.settings.get('Thermal', 'output_name')

    # Concatenate label text and units for the subset of data we actually
    # want to save
    saveKeys = ('read_temp', 'read_input1', 'read_power')
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
  # Also set the thermal controller output to disabled.
  if bLimit:

    currentTemp = responses['read_input1'][0]
    currentUnit = responses['read_input1'][1]
    limitTemp = float(d.settings.get('Thermal', 'power_off_temp'))

    print('Checking thermal limit (--limit)...')

    if (currentTemp < limitTemp):
      print('Passed!  {:.2f} {} is less than {:.2f} {}.\n'.format( currentTemp, 
                                                            currentUnit, 
                                                            limitTemp, 
                                                            currentUnit ) )
    else:

      bLimitExceeded = True
      print('Failed!  {:.2f} {} is over {:.2f} {}.\n'.format( currentTemp, 
                                                            currentUnit, 
                                                            limitTemp, 
                                                            currentUnit ) )


      # Get receiver outlet from settings
      receiverOutlet = int(d.settings.get('Power', 'receiver_outlet'))

      # Send the power switch command to turn off the receiver power
      print('Turning off receiver (on outlet: {})...'.format(receiverOutlet))
      if (d.setOutlet(receiverOutlet, 0)):
        print('Success.')
      else:
        print('Failed.')

      print('\nDisabling thermal controller output...')
      if bEnable:
        print('Skipped because of --enable flag')
      else:
        # Send the thermal controller the disable output command
        if (d.sendThermalCommand('set_output_enabled', arg=0, connection=connection) == 0):
          print('Success.')
        else:
          print('Failed.' )     

    print('')


  # If the start option is set, enable thermal controller output.  
  if bEnable:
    print('Enabling thermal controller output (--enable)...')
    if (d.sendThermalCommand('set_output_enabled', arg=1, connection=connection) == 1):
      print('Success.')
    else:
      print('Failed.' ) 

    print('')

  # If the stop option is set, disable thermal controller output
  if bDisable:
    print('Disabling thermal controller output (--disable)...')
    if (d.sendThermalCommand('set_output_enabled', arg=0, connection=connection) == 0):
      print('Success.')
    else:
      print('Failed.' ) 
    
    print('')

  # If the update option is set, update the thermal controller settings based on 
  #the EDGES configuration settings
  if bUpdate:

    print('Updating onboard thermal controller settings (--update)...\n')

    setKeys = [ 'set_temp', 'set_voltage', 'set_bandwidth', 
                'set_gain', 'set_derivative' ]

    setValues = [float(d.settings.get('Thermal', key)) for key in setKeys]
   
    # Loop over the settings and send them to the thermal controller
    for key, value in zip(setKeys, setValues):

      response = d.sendThermalCommand(key, arg=value, connection=connection)
      unit = thermal_cmds[key][2]

      print("{}: {:.2f} {} : response = {}".format( key.rjust(25), value, 
                                                    unit, response ))

    print('')

  return True
  
   


if __name__ == "__main__":
  checkThermal(sys.argv[1:])
