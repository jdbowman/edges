# -*- coding: utf-8 -*-
import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('..');
import analysis
import models
   
# Data files
inputFile1 = 'C:/Users/jdbowman/Downloads/2018_219_low2_30dB.acq ';
inputFile2 = 'C:/Users/jdbowman/Downloads/2018_220_low2_30dB.acq ';  
fmin = 51;
fmax = 99;

bRead = False;
bPlotResiduals = True;
bPlotMean = True;

inputDir = os.path.dirname(inputFile1);
inputBase = inputFile1[:-5];

# Read the input file
if bRead:
  
  verbose = 1;
  spec1, anc1, freqsfull = analysis.readAcq(inputFile1, verbose=verbose);
  spec2, anc2, freqsfull = analysis.readAcq(inputFile2, verbose=verbose);  
  
  nspec1 = len(spec1);
  nspec2 = len(spec2);
  nfreqsfull = len(freqsfull);

  print('Applying 3-pos switch correction...');
  ta1 = analysis.correct(np.array(spec1[0:nspec1:3]), np.array(spec1[1:nspec1:3]), np.array(spec1[2:nspec1:3]));
  ta2 = analysis.correct(np.array(spec2[0:nspec2:3]), np.array(spec2[1:nspec2:3]), np.array(spec2[2:nspec2:3]));
  nta1 = ta1.shape[0];
  nta2 = ta2.shape[0];
  
print('Integrating...');
ta1Sum = np.sum(ta1, axis=0);   
ta2Sum = np.sum(ta2, axis=0); 
taMean = (ta1Sum + ta2Sum) / (nta1 + nta2);
 
print('Select frequency range...');
indices = np.array(range(nfreqsfull))[(freqsfull>=fmin) & (freqsfull<=fmax)];
taMean = taMean[indices];
freqs = freqsfull[indices];  
nfreqs = len(freqs);

print('Fit polynomial...')
nterms = 3;
components = models.linearPolynomialComponents(freqs, 75, nterms, beta=0);
fit, rms = models.fitLinear(taMean, components);
residuals = taMean - models.linearPolynomial(freqs, 75, fit, beta=0);
kernel = np.ones(60) / 60;
smooth = np.convolve(residuals, kernel, 'same');
print('RMS: {}'.format(rms));


# Make the requested plots
print('Plotting...');
fig = 1;
cmap = 'jet';

if bPlotResiduals:
  
  ymax = np.max(residuals);
  ymin = np.min(residuals);
  ydiff = ymax - ymin;
  ypad = ydiff * 0.1;
  
  plt.figure(fig);
  fig = fig + 1;
  plt.clf();   
  plt.plot(freqs, residuals);
  plt.plot(freqs, smooth);
  plt.xlabel("Frequency [MHz]");
  plt.ylabel("Residuals [K]");
  plt.xlim([fmin, fmax]);
  plt.ylim([ymin-ypad, ymax+ypad]);
  plt.show();
  plt.savefig(inputBase + '_residuals_nterms{}.png'.format(nterms));
  
  
if bPlotMean:

  ymax = np.max(ta1[0,indices]);
  ymin = np.min(ta1[0,indices]);
  ydiff = ymax - ymin;
  ypad = ydiff * 0.1;
  
  plt.figure(fig);
  fig = fig + 1;
  plt.clf();   
  plt.plot(freqs, ta1[0:nta1:100,indices].transpose());
  plt.plot(freqs, ta2[0:nta2:100,indices].transpose());
  plt.plot(freqs, taMean, 'k-');
  plt.xlabel("Frequency [MHz]");
  plt.ylabel("$T_{corrected}$ [K]");
  plt.xlim([fmin, fmax]);
  plt.ylim([ymin-ypad, ymax+ypad]);
  plt.show();
  plt.savefig(inputBase + '_mean.png');

