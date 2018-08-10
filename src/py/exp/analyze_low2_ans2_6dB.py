# -*- coding: utf-8 -*-
import numpy as np
import argparse
import matplotlib.pyplot as plt
import time;
import os
import sys
sys.path.append('..');
import analysis
import models
   
# Data files
inputFile1 = 'C:/Users/jdbowman/Downloads/2018_220_low2.acq ';
inputFile2 = 'C:/Users/jdbowman/Downloads/2018_221_low2.acq ';  
fmin = 51;
fmax = 150;
nterms = 7;
beta = -2.5;

bRead = True;
bPlotResiduals = True;
bPlotMean = True;

inputDir = os.path.dirname(inputFile1);
inputBase = inputFile1[:-5];

# Read the input file
if bRead:
  
  verbose = 1;
  spec1, anc1, freqsfull = analysis.readAcq(inputFile1, verbose=verbose);
  print(spec1[100,8000:8010])
  spec2, anc2, freqsfull = analysis.readAcq(inputFile2, verbose=verbose);  
  print(spec2[100,8000:8010])

  nspec1 = len(spec1);
  nspec2 = len(spec2);
  nfreqsfull = len(freqsfull);

  print('Applying 3-pos switch correction...');

  tic = time.time();
#  ta1 = analysis.correct(spec1[0:nspec1:3], spec1[1:nspec1:3], spec1[2:nspec1:3]);
  ta1 = analysis.correct2(spec1);
  print('Correction time: {} seconds'.format(time.time() - tic));

  tic = time.time();
#  ta2 = analysis.correct(spec2[0:nspec2:3], spec2[1:nspec2:3], spec2[2:nspec2:3]);
  ta2 = analysis.correct2(spec2);
  print('Correction time: {} seconds'.format(time.time() - tic));
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
components = models.linearPolynomialComponents(freqs, 75, nterms, beta=beta);
fit, rms = models.fitLinear(taMean, components);
residuals = taMean - models.linearPolynomial(freqs, 75, fit, beta=beta);
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
  plt.savefig(inputBase + '_3pos_residuals_nterms{}_beta{}_freqs{}-{}.png'.format(nterms, beta, fmin, fmax));
  
  
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
  plt.savefig(inputBase + '_3pos_mean_freqs{}-{}.png'.format(fmin, fmax));

