#!/usr/bin/python

import edges
import argparse
import sys
import os
import glob
import subprocess
from datetime import datetime
import vna
import numpy as np
import matplotlib
matplotlib.use('Agg') # Configure matplotlib to be able to plot straight to file
import matplotlib.pyplot as plt


def antennaS11(argv):
  """
  Acquire OSL and antenna traces through a receiver to produce 
  a calibrated antenna S11 measurement.
  """
  
  # Set default parameter values
  result = True
  parser = argparse.ArgumentParser(description= 'Acquire OSL and antenna traces through the receiver to produce a calibrated antenna S11 measurement.')
  parser.add_argument('folder', help='Output folder to save traces.')
  parser.add_argument('-m', '--message', nargs=1, help='Store a comment with the measurement')
  parser.add_argument('-e', '--external', help='Apply correction from lab measurement of external OSL.  Specify calibration folder')
  parser.add_argument('-f', '--freq', nargs='?', default=75e6, type=float, help='Frequency (Hz) for normalizing the external cal fits')
  parser.add_argument('-n', '--npoly', nargs='?', default=10, type=int, help='Number of polynomial terms in external cal fits')
  parser.add_argument('-p', '--plot', action='store_true', help='Plot the antenna S11')
  parser.add_argument('-r', '--revisit', action='store_true', help='Use existing data in specified folder rather than acquire new traces')
  args = parser.parse_args()

  print args


  # ---------------------------------------------------------------------------
  # Get the EDGES configuration
  # ---------------------------------------------------------------------------

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

  # Set the subdir from the specified folder
  subdir = '{}/{}/s11/{}'.format(site, instrument, args.folder)

  gammas = None

  print('')

  if args.revisit:

    # -------------------------------------------------------------------------
    # Load existing traces for additional work
    # -------------------------------------------------------------------------

    # Look for trace files in the folder
    files = sorted(glob.glob('{}/{}/*_input1.s1p'.format(d.getDataDir(), subdir)))

    if len(files) > 1:
      print('Found multiple trace sets, using first set\n')

    # Get the timestamp
    timestamp = d.parseFileDateString(os.path.split(files[0])[1][:-11])

    print('Using existing traces from: {}\n'.format(timestamp))

    # Get a set of trace files
    inputfiles = []
    inputfiles.append(files[0])
    inputfiles.append('{}_input2.s1p'.format(files[0][:-11]))
    inputfiles.append('{}_input3.s1p'.format(files[0][:-11]))
    inputfiles.append('{}_input4.s1p'.format(files[0][:-11]))

    # Load the trace files
    for index, name in enumerate(inputfiles):
      r, f = vna.s1p_read(name)
      if gammas == None:
        gammas = np.zeros((len(f),4), dtype=np.complex128)
      gammas[:,index] = r

    print('Successfully loaded traces.\n')

  else:

    # -------------------------------------------------------------------------
    # Connect to VNA and acquire new traces
    # -------------------------------------------------------------------------

    # Get the current time
    timestamp = datetime.utcnow()

    print '\nTimestamp: {}'.format(timestamp)

    print('\nReading and writing environmental sensor data...\n')

    # Print the labels and values to stdout
    for l, v, u in zip(labels, values, units):
      print("{}: {:.2f} {}".format(l.rjust(25), v, u))

    # Concatenate label text and units
    fullLabels = ["{} [{}]".format(l, u) for l, u in zip(labels, units)]
	
    # Write to EDGES file record
    result = d.writeRecord(subdir, 'sensors', timestamp, values, fullLabels, breaklevel=5)

    print("")

    # Start the VNA measurements
    session = d.startVNASession()

    # Loop over each OSL+Antenna input
    inputs = {1, 2, 3, 4}
    for i in inputs:

      print('\nAcquiring input {}...'.format(i))

      # Acquire the trace and save it to the subdir
      data = d.getVNATrace(i, session)

      # Write to file
      output_path = d.getFullPath(subdir, 'input{}.s1p'.format(i), timestamp, level=5)
      with open (output_path, "w") as outfile:
        outfile.write(data)
      
      # Add to our array of traces
      r, f = vna.s1p_read_from_text(data)
      if gammas == None:
        gammas = np.zeros((len(f),4), dtype=np.complex128)

      gammas[:,i-1] = r
      
    # Close the VNA session  
    d.stopVNASession(session)

  ## end if args.revisit

  # write comment if there is one
  if args.message:
    result = d.writeText(subdir, 'message', timestamp, args.message[0], 'Message', breaklevel=5)
    print('\nMessage: ' + args.message[0] + '\n') 

  if gammas == None:
    return False

  # ---------------------------------------------------------------------------
  # Apply internal OSL calibration
  # ---------------------------------------------------------------------------
  print('Applying internal OSL correction...\n')

  # Correct the antenna S11 using the OSL inputs
  gammas_internal_corrected = vna.internal_s11_correction(gammas[:,0], gammas[:,1], gammas[:,2], gammas[:,3])

  # Save internally calibrated antenna S11
  output_path = d.getFullPath(subdir, 'antenna_s11.s1p', timestamp, level=5)
  vna.s1p_write(output_path, f, gammas_internal_corrected, 0)

  # ---------------------------------------------------------------------------
  # Apply external OSL calibration (optional)
  # ---------------------------------------------------------------------------
  if args.external != None:
    
    print('Applying (optional) external OSL correction...\n')

    bExternalCorrection = True

    folder_calib = args.external
    subdir_calib = '{}/{}/s11_calibration/{}'.format(site, instrument, folder_calib)

    # The usual internal OSL standards measured at time of external calibration
    int_open, f_int = vna.s1p_read('{}/{}/internal_open.s1p'.format(d.getDataDir(), subdir_calib))
    int_short, f_int = vna.s1p_read('{}/{}/internal_short.s1p'.format(d.getDataDir(), subdir_calib))
    int_load, f_int = vna.s1p_read('{}/{}/internal_load.s1p'.format(d.getDataDir(), subdir_calib))

    # External sources measured through input 4
    ext_open, f_ext = vna.s1p_read('{}/{}/external_open.s1p'.format(d.getDataDir(), subdir_calib))
    ext_short, f_ext = vna.s1p_read('{}/{}/external_short.s1p'.format(d.getDataDir(), subdir_calib))
    ext_load, f_ext = vna.s1p_read('{}/{}/external_load.s1p'.format(d.getDataDir(), subdir_calib))
    resistance_of_match = np.genfromtxt('{}/{}/resistance_of_match.txt'.format(d.getDataDir(), subdir_calib), comments='#')

    # Apply the correction
    gammas_external_corrected = vna.external_s11_correction(
        f, gammas_internal_corrected, 
        f_ext, int_open, int_short, int_load, 
        ext_open, ext_short, ext_load, 
        resistance_of_match, 
        f_norm=args.freq, N_poly_terms=args.npoly)[0]

    # Save externally calibrated antenna S11
    output_path = d.getFullPath(subdir, 'calibrated_{}_antenna_s11.s1p'.format(folder_calib), timestamp, level=5)
    vna.s1p_write(output_path, f, gammas_external_corrected, 0)

  # ---------------------------------------------------------------------------
  # Make output plot and save to PNG
  # ---------------------------------------------------------------------------  
  if args.plot:

    # Plot
    f1 = plt.figure(num=1, figsize=(14, 6))

    plt.subplot(1,2,1)
    plt.plot(f/1e6, 20 * np.log10(np.abs(gammas_internal_corrected)))
    if args.external != None:
      plt.plot(f/1e6, 20 * np.log10(np.abs(gammas_external_corrected)))
    ax = plt.gca()
    ax.set_yticks(np.arange(-50,0,5))
    plt.xlim([40, 200])
    plt.ylim([-50, 0])
    plt.grid()
    plt.xlabel('frequency [MHz]')
    plt.ylabel('magnitude [dB]')

    plt.subplot(1,2,2)
    plt.plot(f/1e6, 180/np.pi * np.unwrap(np.angle(gammas_internal_corrected)))
    if args.external != None:
      plt.plot(f/1e6, 180/np.pi * np.unwrap(np.angle(gammas_external_corrected)))
    plt.xlim([40, 200])
    plt.ylim([-800, 20])
    plt.grid()
    plt.xlabel('frequency [MHz]')
    plt.ylabel('phase [deg]')

    # Save plot
    output_plot = d.getFullPath(subdir, 'antenna_s11.png', timestamp, level=5)
    plt.savefig(output_plot, bbox_inches='tight')
    plt.close(f1)

    # Display plot
    eog_command = 'eog {} &'.format(output_plot)
    subprocess.call(eog_command, shell = True)

 
  if result:
    print('Success.\n')
  else:
    print('Failed.\n')

  return result
    
   


if __name__ == "__main__":
  antennaS11(sys.argv[1:])
