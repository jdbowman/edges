# -*- coding: utf-8 -*-
import numpy as np
import time
import os

# # swpos 2 resolution   24.414 adcmax  0.31476 adcmin -0.32147 temp  0 C nblk 196608 nspec 32768
# 2018:180:14:24:29 2    0.000 0.006104  200.000  0.3 spectrum /tJg/tJ...


# Creates the ASCII to base64 lookup table used by decode.
def getLookupTable():
  
  lookTable = np.zeros(256, dtype=np.int);
  
  for i in range(256):
        
    if (i >= ord('A') and i <= ord('Z')):
      lookTable[i] = i - ord('A');
  
    if (i >= ord('a') and i <= ord('z')):
      lookTable[i] = i - ord('a') + 26;
    
    if (i >= ord('0') and i <= ord('9')):
      lookTable[i] = i - ord('0') + 52;
    
    if (i == ord('+')):
      lookTable[i] = 62;
    
    if (i == ord('/')):
      lookTable[i] = 63;
    
  return lookTable;
    

# ACQ files use base64 encoding (I think) and there is a library in python to 
# encode/decode.  However we also have to pack four bytes back into an a 
# 32-bit integer and then convert from the ACQ units to linear units.  So both
# operations are implemented standalone here.
def decode(input, lookTable):
  
  encodedLength = len(input);
  decodedLength = int(encodedLength / 4);
  
  vals = np.zeros([4,decodedLength], dtype=np.int32);

  inputArray = np.frombuffer(input.encode('ASCII'), dtype=np.uint8);
   
  vals[0,:] = lookTable[inputArray[0:encodedLength:4]];
  vals[1,:] = lookTable[inputArray[1:encodedLength:4]];
  vals[2,:] = lookTable[inputArray[2:encodedLength:4]];
  vals[3,:] = lookTable[inputArray[3:encodedLength:4]];
  
  temp = (vals[0,:]*2**18) +  (vals[1,:]*2**12) + (vals[2,:]*2**6) + vals[3,:];

  return 10.0**(-0.1 * temp * 0.00001);



# Returns some useful information about an ACQ file
def getAcqInfo(inputFile):
  
  # The fundamental unit of an ACQ file is a pair of lines (comment and data)
  # Read the first two lines from the file to get the length of the pair
  with open(inputFile, "r") as acqFile:
    commentRow = acqFile.readline();
    dataRow = acqFile.readline();
  
  # Get the length of the pair of rows in bytes
  pairLength = len(commentRow) + len(dataRow);
    
  # Get the file length
  fileLength = os.path.getsize(inputFile);
  
  # While we're here, check nspec
  nspec = int(commentRow.split()[15]);
          
  return fileLength, pairLength, nspec;


# Read an ACQ file and return the spectra and key ancillary information
# start is the first line of the file to read. Negative values count back from
# the end of the file.
# stop is the last line of the file to read.  Negative values count back from 
# the end of the file.Following the Python convention, stop is exclusive.  For 
# example, Setting start=0 and stop=1 only reads line 0.  
def readAcq(inputFile, start=0, stop=9999999, seek=False, verbose=2):
  
  tic = time.time();
  
  nanc = 13;  
  nlines = 0;
  nspectra = 0;
  lookTable = getLookupTable();  
 
  # Negative start and values give the line from the end of the file.  So we
  # have to convert them to positive values from the beginning of the file.
  fileLength, pairLength, nspec = getAcqInfo(inputFile);
  nlinesInFile = 2.0 * fileLength / pairLength;
  
  if verbose>0:
    print('');
    print('Reading file: {}'.format(inputFile));
    print('Expecting {:} lines in file.'.format(nlinesInFile));
  
  if start < 0:
    start = int(nlinesInFile) + start;
  if stop < 0:
    stop = int(nlinesInFile) + stop;
  if stop>int(nlinesInFile):
    stop = int(nlinesInFile);
  
  nlinesToRead = int(stop - start);
  
  # Allocate arrays for data
  anc = np.zeros([int(nlinesToRead/2), nanc]);
  spectra = np.zeros([int(nlinesToRead/2), nspec], dtype=np.float32);
    
  with open(inputFile, "r") as acqFile:
    
    if start is not 0:
      
      if verbose > 0:
        print('Start flag set to line {}.'.format(start));     
      
      if seek:
        acqFile.seek(int(start * pairLength / 2), 0);
        nlines = start;
        if verbose > 0:
          print('Jumping to start based on estimated line length.')
        
    for line in acqFile:
      
      if (nlines >= stop):
        if verbose > 0:
          print('Stop flag reached at line {}.'.format(nlines));
          break;
        
      if (nlines >= start):
       
        # This is a comment row that preceeds each spectrum line
        if line[0] is '#':
        
          # Parse and remember
          values = line.split();            
          swpos = int(values[2]);
          resolution = float(values[4]);
          adcMax = float(values[6]);
          adcMin = float(values[8]);
          nblock = int(values[13]);
          nspec = int(values[15]);
                
        # This is a data row
        else: 
          
          # Parse
          index = line.index('spectrum') + 9;
          values = line[0:index].split();
          dates = values[0].split(':');
          year = int(dates[0]);
          doy = int( dates[1]);
          hh = int(dates[2]);
          mm = int(dates[3]);
          ss = int(dates[4]);
          sw = int(values[1]);
          channelSize = float(values[3]);
          maxFreq = float(values[4]);
          spectrum = decode(line[index:-1], lookTable);
          
          # Store the comment and data info           
          spectra[nspectra] = spectrum;
          anc[nspectra] = [year, doy, hh, mm, ss, swpos, adcMax, adcMin, nblock, nspec, channelSize, resolution, maxFreq];
          if verbose > 1:
            print('{:} -- swpos: {:}, {:04d}:{:03d} {:02d}:{:02d}:{:02d}, adcmin: {:.3f}, adcmax: {:.3f}'.format(nspectra, swpos, year, doy, hh, mm, ss, adcMin, adcMax));
          
          nspectra = nspectra + 1;
          
      # Increment the number of lines counter
      nlines = nlines + 1;
  
  if verbose > 0:          
    print('Total read: {} lines, {} spectra'.format(nlines-start, nspectra));
  
  # Do some sanity checks
  indswpos = 5;
  if not nlinesInFile.is_integer():
    print('Warning: File length is not an integer multiple of first two lines');
  
  if (nlines % 3) is not 0:
    print('Warning: Total number of lines in file is not a multiple of three');

  if (nspectra % 3) is not 0:
    print('Warning: Total number of spectra read is not a multiple of three');
    
  if int(anc[0, indswpos]) is not 0:
    print('Warning: First read line is not swpos 0');
    
  # Calculate and remember the frequencies once we know the details
  freqs = np.linspace(0, maxFreq, nspec);
          
  if verbose > 0:
    print('Total time: {:.1f} seconds'.format(time.time() - tic));

  return spectra, anc, freqs;


# Apply 3-position switch correction
# p0 is an array of spectra from swpos 0 (antenna)
# p1 is an array of spectra from swpos 1 (ambient load)     
# p2 is an array of spectra from swpos2 (hot load)
def correct(p0, p1, p2, Tcal=400, Tload=300):
  return Tcal * (p0 - p1) / (p2 - p1) + Tload;

def correct2(p, Tcal=400, Tload=300):
  out = np.zeros([int(p.shape[0]/3), p.shape[1]]);
  for i in range(out.shape[0]):
    out[i] = Tcal * (p[0+3*i] - p[1+3*i]) / (p[2+3*i] - p[1+3*i]) + Tload;
  return out;
